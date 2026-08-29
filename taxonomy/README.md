# Knowledge Taxonomy

One folder per **domain**, one JSON file per **discipline**. Folder and file
names are organizational only (keep them snake_case); the display names the
dataset uses come from the JSON fields.

```
taxonomy/
  formal_sciences/            <- domain folder
    cryptography.json         <- one discipline
    graph_theory.json
  physical_sciences/
    thermodynamics.json
  ...
```

Each discipline file:

```json
{
  "domain": "Formal Sciences",
  "discipline": "Cryptography",
  "concepts": [
    "Zero-Knowledge Proof Soundness",
    "Differential Cryptanalysis"
  ]
}
```

## Rules (enforced by the engine at startup)

- Every file in a folder must declare the **same** `domain`, and a domain may
  not be split across two folders.
- No duplicate discipline names within a domain, no duplicate or blank
  concepts within a file.
- Files starting with `_` are ignored — use them for drafts or notes.
- Aim for 5–6 highly technical concepts per discipline; concepts should be
  specific mechanisms ("Write-Ahead Logging"), not broad topics ("Databases").

## Refining over rounds

Add or edit files freely, then rerun the engine. Dataset item ids are
deterministic hashes of (domain, discipline, concept, trajectory), so a rerun
generates only the *new* pairs and resumes everything else from the checkpoint.
Renaming or removing a domain/discipline/concept orphans its old items: they
stay in the checkpoint and keep appearing in the exported dataset. Run the
engine once with `--prune-stale` after such edits to drop every checkpointed
item that no longer matches the current taxonomy.

Validate without generating anything:

```
python distillation_engine.py --list-taxonomy
```
