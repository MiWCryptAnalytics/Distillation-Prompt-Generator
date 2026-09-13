#!/usr/bin/env python3
"""expand_concepts.py — Meta-generation step that grows the taxonomy's concepts.

For every discipline file under taxonomy/, this asks the teacher model to
propose additional highly specific concepts until the file reaches a target
count, deduplicates them against what already exists, validates the result
against the same Pydantic schema the engine uses, and writes it back in place.

It reuses distillation_engine's InferenceClient (retry/backoff/token handling)
and DisciplineFile schema, so the same --backend mock/local/cloud options and
endpoint conventions apply. Run it BEFORE distillation_engine.py: expand the
taxonomy to the depth you want, then generate the dataset over it.

    # Verify the loop with synthetic concepts (writes nothing unless you drop --dry-run):
    python expand_concepts.py --backend mock --target 40 --dry-run

    # Real expansion against a local teacher endpoint:
    python expand_concepts.py --backend local --model Qwen/Qwen3.8-27B --target 40

Each discipline file is rewritten atomically the moment it reaches target, so
the pass is safely resumable: rerun and disciplines already at target are
skipped. Existing concepts are never removed or reordered — only appended to.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

import distillation_engine as engine
from distillation_engine import DisciplineFile, GenerationConfig, CallLogger

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - engine ships the same fallback
    from distillation_engine import tqdm  # type: ignore

log = logging.getLogger("expand_concepts")

SYSTEM_PROMPT = (
    "You are a domain expert building a taxonomy of technical concepts for "
    "advanced study. You produce concise concept names, not explanations."
)

GEN_TEMPLATE = (
    "Discipline: {discipline}\nDomain: {domain}\n\n"
    "Propose {n} additional highly specific concepts within this discipline. "
    "Each must be a concrete mechanism, phenomenon, named result, failure mode, "
    "or technique — NOT a broad topic. Good: 'Xenon-135 Poisoning Transients'. "
    "Bad: 'Nuclear Reactors'. Keep each to a short noun phrase under ~8 words.\n\n"
    "Do NOT repeat any of these already-covered concepts:\n{existing}\n\n"
    "Return ONLY the concept names, one per line, no numbering, no commentary."
)

# Lines that are clearly not concept names (headers, refusals, meta-commentary).
_REJECT = re.compile(r"^(here|sure|certainly|the following|note:|as an|concepts?:)", re.I)


class MockConceptClient(engine.MockClient):
    """Mock backend that emits synthetic concept lines to exercise the loop.

    Each call yields a fresh block of unique names (offset by a per-instance
    counter) so dedup and the top-up loop behave as they would against a real
    model, without any endpoint.
    """

    backend_name = "mock"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._offset = 0

    def _complete(self, messages: list[dict], max_tokens: int) -> tuple[str, str | None]:
        prompt = messages[-1]["content"]
        m = re.search(r"Discipline:\s*(.+)", prompt)
        disc = (m.group(1).strip() if m else "Topic")
        self._offset += 50
        base = self._offset
        return "\n".join(f"{disc} Synthetic Mechanism {base + i}" for i in range(50)), None


def build_client(args: argparse.Namespace) -> engine.InferenceClient:
    config = GenerationConfig(temperature=args.temperature, top_p=args.top_p,
                              max_tokens=args.max_tokens, timeout_s=args.timeout,
                              reasoning_mode=args.reasoning)
    logger = CallLogger(Path(args.call_log) if args.call_log else None)
    if args.backend == "mock":
        return MockConceptClient(args.model or "mock-teacher", config, logger)
    # local / cloud reuse the engine's client construction verbatim.
    return engine.build_client(args, logger)


def parse_concepts(raw: str) -> list[str]:
    out: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        line = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", line)   # strip bullets/numbers
        line = line.strip().strip('"').strip("'").rstrip(".").strip()
        if not line or _REJECT.match(line):
            continue
        if len(line) > 90 or len(line.split()) > 12:            # sentences, not names
            continue
        out.append(line)
    return out


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().casefold()


def expand_file(path: Path, client: engine.InferenceClient, target: int,
                max_rounds: int, dry_run: bool, reserved: set[str]) -> tuple[int, int]:
    """Return (added, final_count). `reserved` holds normalized names claimed
    elsewhere this run when --global-dedup is on (mutated in place)."""
    spec = DisciplineFile.model_validate_json(path.read_text(encoding="utf-8"))
    concepts = list(spec.concepts)
    seen = {norm(c) for c in concepts} | reserved
    start = len(concepts)

    rounds = 0
    while len(concepts) < target and rounds < max_rounds:
        rounds += 1
        need = target - len(concepts)
        prompt = GEN_TEMPLATE.format(
            discipline=spec.discipline, domain=spec.domain,
            n=min(need + 5, 50), existing="\n".join(f"- {c}" for c in concepts))
        raw = client.complete([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]).content
        fresh = 0
        for cand in parse_concepts(raw):
            key = norm(cand)
            if key in seen:
                continue
            seen.add(key)
            concepts.append(cand)
            fresh += 1
            if len(concepts) >= target:
                break
        if fresh == 0:
            log.warning("  %s: no new concepts this round; stopping at %d",
                        spec.discipline, len(concepts))
            break

    concepts = concepts[:target]
    validated = DisciplineFile(domain=spec.domain, discipline=spec.discipline,
                               concepts=concepts)  # revalidate (dedup/blank guard)
    if not dry_run and len(concepts) != start:
        payload = {"domain": validated.domain, "discipline": validated.discipline,
                   "concepts": validated.concepts}
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        os.replace(tmp, path)
    reserved |= {norm(c) for c in validated.concepts}
    return len(concepts) - start, len(concepts)


def run(args: argparse.Namespace) -> int:
    taxonomy_dir = Path(args.taxonomy_dir)
    engine.load_taxonomy(taxonomy_dir)  # validate the whole tree up front
    paths = sorted(p for p in taxonomy_dir.glob("*/*.json") if not p.name.startswith("_"))
    # Filter by domain display name and/or discipline substring.
    def keep(p: Path) -> bool:
        spec = DisciplineFile.model_validate_json(p.read_text(encoding="utf-8"))
        if args.domain and spec.domain not in args.domain:
            return False
        if args.discipline and args.discipline.lower() not in spec.discipline.lower():
            return False
        return True
    paths = [p for p in paths if keep(p)]
    if not paths:
        raise SystemExit("No discipline files match the given filters.")

    client = build_client(args)
    log.info("Backend=%s model=%s | expanding %d discipline(s) to target=%d%s",
             client.backend_name, client.model, len(paths), args.target,
             " (dry-run)" if args.dry_run else "")

    reserved: set[str] = set()
    total_added = at_target = 0
    progress = tqdm(paths, unit="disc", dynamic_ncols=True)
    for path in progress:
        spec = DisciplineFile.model_validate_json(path.read_text(encoding="utf-8"))
        progress.set_description(f"{spec.domain[:18]} / {spec.discipline[:28]}")
        if len(spec.concepts) >= args.target:
            at_target += 1
            reserved |= {norm(c) for c in spec.concepts}
            continue
        try:
            added, final = expand_file(path, client, args.target, args.max_rounds,
                                       args.dry_run, reserved if args.global_dedup else set())
        except engine.InferenceError as exc:
            log.error("FAILED %s: %s (already-written files are preserved)",
                      spec.discipline, exc)
            continue
        total_added += added
    progress.close()

    log.info("Done: +%d concepts across %d discipline(s); %d already at target",
             total_added, len(paths) - at_target, at_target)
    if not args.dry_run:
        tax = engine.load_taxonomy(taxonomy_dir)
        n = sum(len(c) for v in tax.values() for c in v.values())
        log.info("Taxonomy now holds %d concepts across %d disciplines",
                 n, sum(len(v) for v in tax.values()))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Expand each taxonomy discipline to a target concept count "
                    "using the teacher model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--backend", choices=["mock", "local", "cloud"], default="mock")
    p.add_argument("--model", default=None, help="required for local/cloud")
    p.add_argument("--base-url", default=None)
    p.add_argument("--api-key-env", default="OPENAI_API_KEY")
    p.add_argument("--temperature", type=float, default=0.8,
                   help="higher default than generation for concept diversity")
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--reasoning", choices=["capture", "strip", "raw"], default="strip",
                   help="thinking traces are never stored in the taxonomy; "
                        "'strip' keeps call logs lean, 'capture' records them there")
    p.add_argument("--taxonomy-dir", default=str(engine.DEFAULT_TAXONOMY_DIR))
    p.add_argument("--target", type=int, default=40,
                   help="grow each discipline up to this many concepts")
    p.add_argument("--max-rounds", type=int, default=6,
                   help="max model calls per discipline before giving up on top-up")
    p.add_argument("--domain", action="append", help="restrict to a domain (repeatable)")
    p.add_argument("--discipline", default=None, help="restrict to disciplines matching substring")
    p.add_argument("--global-dedup", action="store_true",
                   help="also dedup concepts across disciplines processed this run")
    p.add_argument("--call-log", default=None, help="append raw model calls here (JSONL)")
    p.add_argument("--dry-run", action="store_true", help="do not write files")
    p.add_argument("--log-level", default="INFO",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level),
                        format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
