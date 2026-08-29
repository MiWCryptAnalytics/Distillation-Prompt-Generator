#!/usr/bin/env python3
"""distillation_engine.py — Adversarial dataset engine for model distillation.

Walks a structured taxonomy of human knowledge, generates a two-turn adversarial
conversation for every (concept, trajectory) pair by querying a teacher model,
and writes a fine-tuning-ready dataset validated against a strict Pydantic schema.

The taxonomy lives in the taxonomy/ directory (one folder per domain, one JSON
file per discipline — see taxonomy/README.md) and is validated at startup.

Backends (selected with --backend):
    mock   Instant dummy responses. Verifies the taxonomy loop, checkpointing,
           and schema generation without any endpoint or extra dependencies.
    local  OpenAI-compatible endpoint on localhost (vLLM / TGI / llama.cpp
           server hosting e.g. Qwen-2.5-14B or Gemma-2-9B).
    cloud  Any hosted OpenAI-compatible API (requires an API key in the
           environment; see --api-key-env).

Usage:
    python distillation_engine.py --backend mock --limit 12
    python distillation_engine.py --backend local \
        --base-url http://localhost:8000/v1 --model Qwen/Qwen2.5-14B-Instruct
    python distillation_engine.py --backend cloud \
        --base-url https://api.example.com/v1 --model my-teacher \
        --api-key-env TEACHER_API_KEY

Progress is checkpointed after every completed item to a JSONL file next to the
output; rerunning the same command resumes where the previous run stopped. Every
raw inference call (prompt messages, sampling config, raw output) is appended to
a call log for auditability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import random
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

from pydantic import BaseModel, Field, model_validator

try:
    from tqdm import tqdm
except ImportError:  # degrade gracefully: plain iteration with log lines
    class tqdm:  # type: ignore[no-redef]
        def __init__(self, iterable=None, total=None, **_):
            self._iterable = iterable if iterable is not None else []

        def __iter__(self):
            return iter(self._iterable)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def set_description(self, desc):
            logging.info("%s", desc)

        def update(self, *_):
            pass

        def close(self):
            pass

log = logging.getLogger("distillation_engine")

# ---------------------------------------------------------------------------
# 1. Adversarial trajectory templates (high-fidelity, anti-surface-level)
# ---------------------------------------------------------------------------

ADVERSARIAL_TRAJECTORY_TEMPLATES = {
    "who_agency": (
        "Identify the primary operational agent, hidden dependency, or system driver in {concept}. "
        "Analyze its specific intent, systemic leverage, and the boundaries of its autonomy. "
        "Contrast its role with an alternative or adversarial agent attempting to disrupt this system."
    ),
    "what_mechanics": (
        "Deconstruct {concept} into its raw, structural components without using surface analogies or metaphors. "
        "Explain the exact information, energy, or logical state transfer occurring between these components. "
        "What specific structural element represents the single point of failure?"
    ),
    "where_boundaries": (
        "Isolate the precise theoretical, systemic, or physical boundaries where {concept} breaks down entirely. "
        "Describe the catastrophic failure mode or mathematical divergence that occurs when these boundaries are crossed. "
        "Why is it impossible to scale past this point?"
    ),
    "when_dependencies": (
        "Construct a granular, chronological dependency chain required to instantiate or activate {concept}. "
        "What race conditions, latency bottlenecks, or state prerequisites must be perfectly met? "
        "Explain how the system handles a failure or delay in any single step of this sequence."
    ),
    "why_teleology": (
        "Expose the fundamental causal vectors and first-principles trade-offs that justify the existence of {concept}. "
        "Why is this specific structural design chosen over mathematically or systemically cheaper alternatives? "
        "Expose the inherent flaws or debt this design compromises on."
    ),
    "how_adversarial": (
        "Design a high-impact adversarial edge case, Byzantine fault, or systemic exploit targeting {concept}. "
        "Provide a step-by-step breakdown of how the exploit cascades through the system. "
        "Detail the exact diagnostic signals or telemetry indicators that would confirm this systemic failure is underway."
    ),
    "compare_contrast": (
        "Place {concept} in direct opposition to its closest structural rival or alternative implementation. "
        "Enumerate the precise tradeoff surface: what each buys, what each forfeits, and the exact regime where one dominates. "
        "Identify the single decision variable that should flip an expert's choice between them."
    ),
    "historical_evolution": (
        "Reconstruct how the modern understanding of {concept} was reached, including the abandoned models and the "
        "specific anomalies that killed them. Pinpoint the conceptual breakthrough or reframing that resolved the prior impasse. "
        "Which now-dominant assumption is the most likely candidate to be overturned next, and why?"
    ),
    "quantitative_scaling": (
        "Expose the governing quantitative relationships of {concept}: the scaling laws, dimensionless ratios, and orders "
        "of magnitude that actually constrain it. Identify which variable dominates as the system scales, and where a linear "
        "intuition breaks down catastrophically. Give the back-of-the-envelope estimate an expert uses to sanity-check a claim about it."
    ),
    "cross_domain_transfer": (
        "Map the underlying structure of {concept} onto a distant, unrelated domain where the same formal pattern appears. "
        "Make the isomorphism precise — what corresponds to what — then identify exactly where the analogy breaks and becomes misleading. "
        "What non-obvious insight transfers back to {concept} from that distant domain?"
    ),
    "misconception_diagnosis": (
        "Identify the most seductive misconception about {concept} that even trained practitioners hold, and dissect why it persists. "
        "Trace the precise reasoning error or hidden assumption that generates it. "
        "Construct the minimal example or experiment that decisively exposes the misconception."
    ),
    "operationalization": (
        "Specify how {concept} would actually be measured, detected, or instrumented in the real world. "
        "Identify the proxy signals used when it cannot be observed directly, and the systematic errors those proxies introduce. "
        "What confound would most easily fool an observer into believing {concept} is present when it is not?"
    ),
}

TURN1_TEMPLATE = (
    "Explain the foundational theory of {concept} in the context of {discipline}."
)

# ---------------------------------------------------------------------------
# 2. Broad human knowledge taxonomy, loaded from the taxonomy/ directory
# ---------------------------------------------------------------------------
#
# Layout: one folder per domain, one JSON file per discipline:
#
#     taxonomy/
#       formal_sciences/
#         cryptography.json   -> {"domain": "Formal Sciences",
#                                 "discipline": "Cryptography",
#                                 "concepts": ["...", ...]}
#
# Folder and file names are organizational only; display names come from the
# JSON fields. Add or edit files and rerun: item ids are deterministic, so only
# new (concept, trajectory) pairs are generated and the rest resume from the
# checkpoint.

DEFAULT_TAXONOMY_DIR = Path(__file__).resolve().parent / "taxonomy"

Taxonomy = dict[str, dict[str, list[str]]]


class DisciplineFile(BaseModel):
    """Schema of one taxonomy/<domain>/<discipline>.json file."""

    domain: str = Field(min_length=1)
    discipline: str = Field(min_length=1)
    concepts: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _clean_concepts(self) -> "DisciplineFile":
        cleaned = [c.strip() for c in self.concepts]
        if any(not c for c in cleaned):
            raise ValueError("concepts must not be blank")
        duplicates = sorted({c for c in cleaned if cleaned.count(c) > 1})
        if duplicates:
            raise ValueError(f"duplicate concepts: {duplicates}")
        self.concepts = cleaned
        return self


def load_taxonomy(taxonomy_dir: Path) -> Taxonomy:
    """Load and validate the taxonomy from <taxonomy_dir>/<domain>/<discipline>.json.

    Collects every problem found (bad JSON, schema violations, duplicate
    disciplines, a domain split across folders, or one folder declaring two
    domains) and fails loudly rather than generating a partial dataset.
    Files whose names start with "_" are ignored (drafts, notes).
    """
    if not taxonomy_dir.is_dir():
        raise SystemExit(
            f"Taxonomy directory not found: {taxonomy_dir}\n"
            "Expected one folder per domain containing one JSON file per "
            "discipline, e.g. taxonomy/formal_sciences/cryptography.json with "
            '{"domain": ..., "discipline": ..., "concepts": [...]}'
        )
    paths = sorted(p for p in taxonomy_dir.glob("*/*.json")
                   if not p.name.startswith("_"))
    if not paths:
        raise SystemExit(f"No discipline files (*/*.json) found under {taxonomy_dir}")

    taxonomy: Taxonomy = {}
    folder_domain: dict[str, str] = {}   # folder name -> domain declared inside it
    domain_folder: dict[str, str] = {}   # domain name -> folder (1:1 enforced)
    errors: list[str] = []
    for file_path in paths:
        rel = file_path.relative_to(taxonomy_dir)
        try:
            spec = DisciplineFile.model_validate_json(
                file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel}: {exc}")
            continue
        folder = file_path.parent.name
        if folder_domain.setdefault(folder, spec.domain) != spec.domain:
            errors.append(f"{rel}: declares domain {spec.domain!r} but folder "
                          f"{folder}/ already holds {folder_domain[folder]!r}")
            continue
        if domain_folder.setdefault(spec.domain, folder) != folder:
            errors.append(f"{rel}: domain {spec.domain!r} is split across folders "
                          f"{domain_folder[spec.domain]}/ and {folder}/")
            continue
        disciplines = taxonomy.setdefault(spec.domain, {})
        if spec.discipline in disciplines:
            errors.append(f"{rel}: duplicate discipline {spec.discipline!r} "
                          f"in domain {spec.domain!r}")
            continue
        disciplines[spec.discipline] = spec.concepts
    if errors:
        raise SystemExit("Taxonomy validation failed:\n  " + "\n  ".join(errors))
    return taxonomy

# ---------------------------------------------------------------------------
# 3. Strict dataset schema (Pydantic-enforced)
# ---------------------------------------------------------------------------

TRAJECTORY_NAMES = tuple(ADVERSARIAL_TRAJECTORY_TEMPLATES)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ItemMetadata(BaseModel):
    domain: str
    discipline: str
    concept: str
    trajectory: str

    @model_validator(mode="after")
    def _known_trajectory(self) -> "ItemMetadata":
        if self.trajectory not in ADVERSARIAL_TRAJECTORY_TEMPLATES:
            raise ValueError(f"unknown trajectory: {self.trajectory!r}")
        return self


class TrajectoryItem(BaseModel):
    id: str = Field(min_length=8)
    metadata: ItemMetadata
    messages: list[Message]

    @model_validator(mode="after")
    def _valid_conversation(self) -> "TrajectoryItem":
        roles = [m.role for m in self.messages]
        if roles != ["user", "assistant", "user", "assistant"]:
            raise ValueError(f"messages must be a 2-turn u/a/u/a conversation, got roles {roles}")
        if any(not m.content.strip() for m in self.messages):
            raise ValueError("messages must not be blank")
        return self


@dataclass(frozen=True)
class WorkItem:
    """One (concept, trajectory) pair to be turned into a TrajectoryItem."""

    domain: str
    discipline: str
    concept: str
    trajectory: str

    @property
    def id(self) -> str:
        key = f"{self.domain}|{self.discipline}|{self.concept}|{self.trajectory}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]

    @property
    def path_label(self) -> str:
        return f"[{self.domain} -> {self.concept} -> {self.trajectory}]"


def enumerate_work(
    taxonomy: Taxonomy,
    domains: list[str] | None = None,
    trajectories: list[str] | None = None,
) -> Iterator[WorkItem]:
    wanted_trajectories = trajectories or list(TRAJECTORY_NAMES)
    for domain, disciplines in taxonomy.items():
        if domains and domain not in domains:
            continue
        for discipline, concepts in disciplines.items():
            for concept in concepts:
                for trajectory in wanted_trajectories:
                    yield WorkItem(domain, discipline, concept, trajectory)


# ---------------------------------------------------------------------------
# 4. Inference clients
# ---------------------------------------------------------------------------


class InferenceError(Exception):
    """Unrecoverable inference failure for one call (after retries)."""


class TransientError(Exception):
    """Timeout / connection / rate-limit failure worth retrying with backoff."""


class TokenLimitError(Exception):
    """The request exceeded the model's context or output token limits."""


@dataclass
class GenerationConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    timeout_s: float = 120.0


class CallLogger:
    """Appends one JSON line per raw inference call: prompt, config, output."""

    def __init__(self, path: Path | None):
        self.path = path

    def record(self, *, backend: str, model: str, config: GenerationConfig,
               max_tokens_used: int, messages: list[dict], response: str,
               attempts: int, elapsed_s: float) -> None:
        if self.path is None:
            return
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "backend": backend,
            "model": model,
            "config": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_tokens": max_tokens_used,
                "timeout_s": config.timeout_s,
            },
            "messages": messages,
            "response": response,
            "attempts": attempts,
            "elapsed_s": round(elapsed_s, 3),
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


class InferenceClient(ABC):
    """Teacher-model client with retry, backoff, and token-overflow recovery."""

    backend_name = "abstract"
    TRANSIENT_RETRIES = 5
    BACKOFF_BASE_S = 2.0
    BACKOFF_CAP_S = 60.0
    MIN_MAX_TOKENS = 256
    MAX_CONTEXT_TRUNCATIONS = 2

    def __init__(self, model: str, config: GenerationConfig, call_logger: CallLogger):
        self.model = model
        self.config = config
        self.call_logger = call_logger

    @abstractmethod
    def _complete(self, messages: list[dict], max_tokens: int) -> str:
        """Single raw completion attempt. Raises TransientError / TokenLimitError."""

    def complete(self, messages: list[dict]) -> str:
        max_tokens = self.config.max_tokens
        transient_attempts = 0
        truncations = 0
        total_attempts = 0
        started = time.monotonic()
        while True:
            total_attempts += 1
            try:
                text = self._complete(messages, max_tokens)
                if not text or not text.strip():
                    raise TransientError("model returned an empty completion")
                text = text.strip()
                self.call_logger.record(
                    backend=self.backend_name, model=self.model, config=self.config,
                    max_tokens_used=max_tokens, messages=messages, response=text,
                    attempts=total_attempts, elapsed_s=time.monotonic() - started,
                )
                return text
            except TokenLimitError as exc:
                if max_tokens > self.MIN_MAX_TOKENS:
                    max_tokens = max(self.MIN_MAX_TOKENS, max_tokens // 2)
                    log.warning("Token limit hit (%s); retrying with max_tokens=%d", exc, max_tokens)
                elif truncations < self.MAX_CONTEXT_TRUNCATIONS:
                    truncations += 1
                    messages = self._truncate_longest(messages)
                    log.warning("Token limit persists; truncated longest context message "
                                "(truncation %d/%d)", truncations, self.MAX_CONTEXT_TRUNCATIONS)
                else:
                    raise InferenceError(f"token limit overflow not recoverable: {exc}") from exc
            except TransientError as exc:
                transient_attempts += 1
                if transient_attempts > self.TRANSIENT_RETRIES:
                    raise InferenceError(
                        f"gave up after {self.TRANSIENT_RETRIES} retries: {exc}"
                    ) from exc
                delay = min(self.BACKOFF_CAP_S, self.BACKOFF_BASE_S ** transient_attempts)
                delay *= 0.5 + random.random() / 2  # jitter
                log.warning("Transient inference failure (%s); retry %d/%d in %.1fs",
                            exc, transient_attempts, self.TRANSIENT_RETRIES, delay)
                time.sleep(delay)

    @staticmethod
    def _truncate_longest(messages: list[dict]) -> list[dict]:
        idx = max(range(len(messages)), key=lambda i: len(messages[i]["content"]))
        clipped = dict(messages[idx])
        clipped["content"] = clipped["content"][: max(200, len(clipped["content"]) // 2)] \
            + "\n…[truncated to fit context window]"
        return [clipped if i == idx else m for i, m in enumerate(messages)]


class MockClient(InferenceClient):
    """Instant dummy responses for verifying loop structure and schema output."""

    backend_name = "mock"

    def _complete(self, messages: list[dict], max_tokens: int) -> str:
        prompt = messages[-1]["content"]
        return (
            f"[MOCK {self.model}] turn={len(messages) // 2 + 1} "
            f"context_msgs={len(messages)} max_tokens={max_tokens} :: "
            f"Simulated teacher response to: {prompt[:140]}"
        )


class OpenAICompatibleClient(InferenceClient):
    """Chat-completions client for any OpenAI-compatible endpoint.

    Covers both the `local` backend (vLLM / TGI / llama.cpp server hosting
    Qwen or Gemma) and the `cloud` backend (hosted APIs speaking the same
    protocol) — only base_url / api_key differ.
    """

    def __init__(self, model: str, config: GenerationConfig, call_logger: CallLogger,
                 base_url: str | None, api_key: str, backend_name: str):
        super().__init__(model, config, call_logger)
        self.backend_name = backend_name
        try:
            import openai
        except ImportError as exc:
            raise SystemExit(
                "The 'openai' package is required for --backend local/cloud "
                "(pip install openai). Mock mode needs no extra dependencies."
            ) from exc
        self._openai = openai
        self._client = openai.OpenAI(
            base_url=base_url, api_key=api_key, timeout=config.timeout_s, max_retries=0,
        )

    def _complete(self, messages: list[dict], max_tokens: int) -> str:
        oa = self._openai
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=max_tokens,
            )
        except (oa.APITimeoutError, oa.APIConnectionError, oa.RateLimitError,
                oa.InternalServerError) as exc:
            raise TransientError(str(exc)) from exc
        except oa.BadRequestError as exc:
            msg = str(exc).lower()
            if "context" in msg or "token" in msg or "length" in msg:
                raise TokenLimitError(str(exc)) from exc
            raise InferenceError(f"bad request: {exc}") from exc
        except oa.APIStatusError as exc:
            raise InferenceError(f"API error {exc.status_code}: {exc}") from exc

        if not resp.choices:
            raise TransientError("response contained no choices")
        content = resp.choices[0].message.content
        if content is None:
            raise TransientError("response choice had no content")
        return content


def build_client(args: argparse.Namespace, call_logger: CallLogger) -> InferenceClient:
    config = GenerationConfig(
        temperature=args.temperature, top_p=args.top_p,
        max_tokens=args.max_tokens, timeout_s=args.timeout,
    )
    if args.backend == "mock":
        return MockClient(args.model or "mock-teacher", config, call_logger)

    if not args.model:
        raise SystemExit(f"--model is required for --backend {args.backend} "
                         "(e.g. Qwen/Qwen2.5-14B-Instruct)")
    if args.backend == "local":
        base_url = args.base_url or "http://localhost:8000/v1"
        api_key = os.environ.get(args.api_key_env, "") or "EMPTY"  # vLLM convention
    else:  # cloud
        base_url = args.base_url  # None -> the openai package's default endpoint
        api_key = os.environ.get(args.api_key_env, "")
        if not api_key:
            raise SystemExit(f"--backend cloud requires an API key in ${args.api_key_env}")
    return OpenAICompatibleClient(
        args.model, config, call_logger,
        base_url=base_url, api_key=api_key, backend_name=args.backend,
    )


# ---------------------------------------------------------------------------
# 5. Checkpointed dataset store
# ---------------------------------------------------------------------------


class CheckpointStore:
    """Append-only JSONL checkpoint with atomic final JSON export.

    Every completed TrajectoryItem is flushed to the checkpoint file the moment
    it is generated, so a crash or interrupt mid-taxonomy loses at most the
    item in flight. On startup, existing checkpoint lines are validated and
    loaded so the run resumes exactly where it stopped.
    """

    def __init__(self, path: Path):
        self.path = path
        self.items: dict[str, TrajectoryItem] = {}
        if path.exists():
            self._load()

    def _load(self) -> None:
        bad_lines = 0
        with self.path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = TrajectoryItem.model_validate_json(line)
                    self.items[item.id] = item
                except Exception:
                    bad_lines += 1
                    log.warning("Skipping corrupt checkpoint line %d in %s "
                                "(likely a partial write)", line_no, self.path)
        if bad_lines:
            log.warning("%d corrupt checkpoint line(s) ignored; those items will regenerate",
                        bad_lines)
        if self.items:
            log.info("Resumed %d completed item(s) from %s", len(self.items), self.path)

    @property
    def completed_ids(self) -> set[str]:
        return set(self.items)

    def add(self, item: TrajectoryItem) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(item.model_dump_json() + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        self.items[item.id] = item

    def prune(self, valid_ids: set[str]) -> int:
        """Drop items not in valid_ids and rewrite the checkpoint atomically."""
        stale = [item_id for item_id in self.items if item_id not in valid_ids]
        if not stale:
            return 0
        for item_id in stale:
            del self.items[item_id]
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            for item in self.items.values():
                fh.write(item.model_dump_json() + "\n")
        os.replace(tmp_path, self.path)
        return len(stale)

    def export(self, out_path: Path) -> int:
        ordered = sorted(
            self.items.values(),
            key=lambda it: (it.metadata.domain, it.metadata.discipline,
                            it.metadata.concept, it.metadata.trajectory),
        )
        payload = [it.model_dump() for it in ordered]
        tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp_path, out_path)  # atomic: never leaves a half-written dataset
        return len(payload)


# ---------------------------------------------------------------------------
# 6. Generation loop
# ---------------------------------------------------------------------------


def generate_item(client: InferenceClient, work: WorkItem) -> TrajectoryItem:
    conversation: list[dict] = [{
        "role": "user",
        "content": TURN1_TEMPLATE.format(concept=work.concept, discipline=work.discipline),
    }]
    conversation.append({"role": "assistant", "content": client.complete(conversation)})
    conversation.append({
        "role": "user",
        "content": ADVERSARIAL_TRAJECTORY_TEMPLATES[work.trajectory].format(concept=work.concept),
    })
    conversation.append({"role": "assistant", "content": client.complete(conversation)})
    return TrajectoryItem(
        id=work.id,
        metadata=ItemMetadata(
            domain=work.domain, discipline=work.discipline,
            concept=work.concept, trajectory=work.trajectory,
        ),
        messages=[Message(**m) for m in conversation],
    )


def run(args: argparse.Namespace) -> int:
    output_path = Path(args.output)
    # Backend-specific default so a mock dry run can never be "resumed" into a
    # real run (item ids are deterministic across backends).
    checkpoint_path = Path(args.checkpoint) if args.checkpoint else \
        output_path.with_suffix(f".{args.backend}.checkpoint.jsonl")
    call_log_path = None if args.no_call_log else \
        (Path(args.call_log) if args.call_log else output_path.with_suffix(".calls.jsonl"))

    taxonomy = load_taxonomy(Path(args.taxonomy_dir))
    unknown_domains = sorted(set(args.domain or []) - set(taxonomy))
    if unknown_domains:
        raise SystemExit(f"Unknown domain(s) {unknown_domains}. "
                         f"Available: {sorted(taxonomy)}")
    work = list(enumerate_work(taxonomy, domains=args.domain or None,
                               trajectories=args.trajectory or None))
    if args.limit:
        work = work[: args.limit]
    if not work:
        raise SystemExit("No work items match the given --domain/--trajectory filters.")

    store = CheckpointStore(checkpoint_path)
    if args.prune_stale:
        # Judge staleness against the FULL taxonomy, not the filtered work list,
        # so --domain/--trajectory/--limit runs never prune out-of-scope items.
        valid_ids = {w.id for w in enumerate_work(taxonomy)}
        pruned = store.prune(valid_ids)
        log.info("Pruned %d stale checkpoint item(s) no longer in the taxonomy", pruned)
    client = build_client(args, CallLogger(call_log_path))
    done = store.completed_ids

    log.info("Backend=%s model=%s | %d work item(s), %d already complete",
             client.backend_name, client.model, len(work), sum(w.id in done for w in work))

    generated = skipped = failed = 0
    consecutive_failures = 0
    aborted_reason: str | None = None

    progress = tqdm(work, unit="item", dynamic_ncols=True)
    try:
        for item_spec in progress:
            progress.set_description(f"Processing {item_spec.path_label}"[:100])
            if item_spec.id in done:
                skipped += 1
                continue
            try:
                item = generate_item(client, item_spec)
            except InferenceError as exc:
                failed += 1
                consecutive_failures += 1
                log.error("FAILED %s: %s", item_spec.path_label, exc)
                if consecutive_failures >= args.max_consecutive_failures:
                    aborted_reason = (
                        f"{consecutive_failures} consecutive failures — the inference "
                        "endpoint looks down. Completed items are checkpointed; rerun to resume."
                    )
                    break
                continue
            consecutive_failures = 0
            store.add(item)  # flushed to disk immediately — crash-safe
            generated += 1
    except KeyboardInterrupt:
        aborted_reason = "Interrupted by user. Completed items are checkpointed; rerun to resume."
    finally:
        progress.close()
        total = store.export(output_path)
        log.info("Dataset export: %d validated item(s) -> %s", total, output_path)

    log.info("Run summary: %d generated, %d resumed/skipped, %d failed (of %d planned)",
             generated, skipped, failed, len(work))
    if aborted_reason:
        log.warning("Run stopped early: %s", aborted_reason)
        return 1
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# 7. CLI
# ---------------------------------------------------------------------------


def print_taxonomy(taxonomy: Taxonomy) -> None:
    total_concepts = 0
    for domain, disciplines in taxonomy.items():
        print(f"{domain}")
        for discipline, concepts in disciplines.items():
            print(f"  {discipline}: {len(concepts)} concepts")
            total_concepts += len(concepts)
    n_traj = len(ADVERSARIAL_TRAJECTORY_TEMPLATES)
    print(f"\n{total_concepts} concepts x {n_traj} trajectories = "
          f"{total_concepts * n_traj} dataset items "
          f"({total_concepts * n_traj * 2} teacher calls)")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an adversarial multi-turn distillation dataset "
                    "from a taxonomy of human knowledge.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--backend", choices=["mock", "local", "cloud"], default="mock",
                        help="teacher inference backend")
    parser.add_argument("--model", default=None,
                        help="teacher model name (required for local/cloud)")
    parser.add_argument("--base-url", default=None,
                        help="OpenAI-compatible endpoint URL "
                             "(local default: http://localhost:8000/v1)")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY",
                        help="environment variable holding the API key")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--max-tokens", type=int, default=2048,
                        help="max completion tokens per teacher call")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="per-call timeout in seconds")
    parser.add_argument("--output", default="adversarial_distillation_dataset.json",
                        help="final dataset path")
    parser.add_argument("--checkpoint", default=None,
                        help="checkpoint JSONL path "
                             "(default: <output>.<backend>.checkpoint.jsonl)")
    parser.add_argument("--call-log", default=None,
                        help="raw inference call log path (default: <output>.calls.jsonl)")
    parser.add_argument("--no-call-log", action="store_true",
                        help="disable the raw call log")
    parser.add_argument("--taxonomy-dir", default=str(DEFAULT_TAXONOMY_DIR),
                        help="root of the domain-folder taxonomy")
    parser.add_argument("--domain", action="append", metavar="NAME",
                        help="restrict to a domain display name (repeatable)")
    parser.add_argument("--trajectory", action="append", choices=list(TRAJECTORY_NAMES),
                        help="restrict to a trajectory (repeatable)")
    parser.add_argument("--limit", type=int, default=0,
                        help="cap the number of work items (0 = no cap)")
    parser.add_argument("--max-consecutive-failures", type=int, default=5,
                        help="abort after this many consecutive item failures")
    parser.add_argument("--prune-stale", action="store_true",
                        help="drop checkpointed items whose taxonomy entry was "
                             "renamed or removed, then continue")
    parser.add_argument("--list-taxonomy", action="store_true",
                        help="print taxonomy statistics and exit")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )
    if args.list_taxonomy:
        print_taxonomy(load_taxonomy(Path(args.taxonomy_dir)))
        return 0
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
