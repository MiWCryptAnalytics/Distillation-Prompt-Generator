# Adversarial Knowledge Distillation Pipeline

Generate deep, multi-turn training conversations across the breadth of human
knowledge — for distilling large "teacher" models into open-weights students
(Qwen, Gemma, etc.).

A hand-curated taxonomy of **11 domains → 613 disciplines → 3,623 seed
concepts** is crossed with **12 adversarial prompt trajectories** (failure
modes, edge cases, misconceptions, scaling limits, …) to produce two-turn
conversations that force a teacher model past textbook summaries and into its
actual reasoning — the "dark knowledge" worth distilling.

```
taxonomy/                 expand_concepts.py            distillation_engine.py
domain/discipline JSONs ──► grow each discipline ──────► concept × trajectory
(hand-curated skeleton)     to N concepts (teacher-      conversations, validated
                            generated, deduped)          + checkpointed → dataset
```

## Quickstart

```bash
pip install -r requirements.txt

# 1. Verify the loop end-to-end with no endpoint (instant, writes a real dataset):
python distillation_engine.py --backend mock --limit 20

# 2. Optionally deepen the taxonomy against your teacher endpoint first:
python expand_concepts.py --backend local --model Qwen/Qwen3.8-27B --target 40

# 3. Generate the dataset:
python distillation_engine.py --backend local --model Qwen/Qwen3.8-27B
```

Backends: `mock` (no dependencies, structural verification), `local` (any
OpenAI-compatible endpoint — vLLM, TGI, llama.cpp; defaults to
`http://localhost:8000/v1`), `cloud` (hosted OpenAI-compatible APIs;
key via `--api-key-env`).

Every completed item is checkpointed immediately; rerun the same command to
resume. `--domain`/`--trajectory`/`--limit` slice the run, `--list-taxonomy`
validates and prints the tree, `--prune-stale` cleans up after renames.

## Scale

| Stage | Items (2-turn conversations) |
|---|---|
| Seed concepts as-is | 3,623 × 12 = 43,476 |
| After `expand_concepts.py --target 30` | ~220,000 |
| After `--target 40` | ~294,000 |

Each item costs two teacher calls. The output is JSON in standard
`messages` chat format with full domain/discipline/concept/trajectory metadata
per item — see the schema enforced in `distillation_engine.py` (Pydantic).

**Reasoning capture**: when the teacher thinks out loud, assistant turns gain
an optional `reasoning` field holding the trace — training on reasoning
transfers the *process*, not just the conclusions. `--reasoning capture` (the
default) handles both delivery mechanisms: separated reasoning (vLLM
`--reasoning-parser`) and inline `<think>` blocks; `strip` removes thinking,
`raw` passes content through untouched. Context sent back to the teacher is
always kept clean of traces.

## Repository layout

| Path | What it is |
|---|---|
| `distillation_engine.py` | Dataset generator: taxonomy × trajectories → validated, checkpointed dataset |
| `expand_concepts.py` | Meta-generator: grows each discipline's concept list via the teacher model |
| `taxonomy/` | The knowledge taxonomy — one folder per domain, one JSON file per discipline |
| `taxonomy/README.md` | Taxonomy file format and editing rules |
| `taxonomy/<domain>/_coverage.md` | Per-domain map to DDC/LCC/OECD/ACM/JEL anchors + known gaps |
| `taxonomy/_audits.md` | Registry of external catalogs the taxonomy has been audited against |
| `PHILOSOPHY.yaml` | Machine-readable design principles and research direction |

## Design in one paragraph

Breadth over depth, mechanisms over topics. The discipline skeleton is
hand-curated and audited against six independent classification systems
(Dewey, Library of Congress, OECD Frascati, ACM, BLS SOC, ISCO-08 — see
`taxonomy/_audits.md`); the concept leaves are teacher-generated at scale with
dedup and schema validation. Every concept is a specific mechanism, failure
mode, or named result ("Xenon-135 Poisoning Transients", not "Nuclear
Reactors"), because that is the grain at which adversarial prompts extract
expert reasoning rather than encyclopedia prose. Full rationale in
[PHILOSOPHY.yaml](PHILOSOPHY.yaml).

## Notes

- **Teacher licensing**: distill only from models whose terms permit it (e.g.
  self-hosted Qwen/Gemma). Several API providers, including Anthropic, prohibit
  using outputs to train competing models.
- Trajectories that ask for "exploits" or "failure modes" are pedagogical
  devices aimed at academic concepts; review generated content before release.
- Code and taxonomy are released under the [MIT License](LICENSE). Datasets you
  generate with it are yours; their terms depend on your teacher model's license.
