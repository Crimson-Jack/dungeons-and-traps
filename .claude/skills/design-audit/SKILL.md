---
name: design-audit
description: Read-only code-design audit of given files/directories (size/SRP, property vs methods, testability, duplication, Python idioms) producing a backlog ranked by gain/risk for code_design_improvements-part_N.md. Use when asked for a design review or before a larger refactor. Not for diff/bug review — that is /code-review.
argument-hint: <files or directories, e.g. src/game.py src/sprites/>
allowed-tools: Read, Grep, Glob, Bash(venv/Scripts/python.exe -m radon:*), Bash(venv/Scripts/python.exe -m ruff check:*)
---

# Design audit

Audit the code design of: `$ARGUMENTS`

## 1. Scope

- Audit only the files/directories given above.
- If no scope is given, ask for one. Do not audit the whole `src/` by default.

## 2. Hard rule

You do not edit, create, or delete any file. The only output is the report.

## 3. Measure first

Run the metrics from `requirements-dev.txt` (radon, ruff) on the scope, from the project root:

```
venv/Scripts/python.exe -m radon cc -s -n C <scope>
venv/Scripts/python.exe -m radon mi -s <scope>
venv/Scripts/python.exe -m radon raw -s <scope>
venv/Scripts/python.exe -m ruff check --no-fix --output-format concise --select C901,PLR0911,PLR0912,PLR0913,PLR0915,SIM,RET,UP,F401,F841,ERA <scope>
```

- `radon cc -n C` — cyclomatic complexity, ranks C–F only.
- `radon mi` — maintainability index.
- `radon raw` — LOC / SLOC.
- `ruff check` — complexity, too many arguments/branches/returns/statements, simplifications,
  `else` after `return`, outdated idioms, unused imports/variables, commented-out code.
  Rules are passed via `--select` because the project has no ruff config.

Never run `ruff` with `--fix`, never run `ruff format`, never redirect output to files.

Metrics verify and rank findings — they do not replace reading the code:
- Every candidate flagged by the metrics is read (`Read`) and assessed against the rubric.
- A rubric finding without metric evidence is allowed (e.g. property vs method).
- A rank C+ function or a low-MI file left unassessed in the report is not.
- If the tools cannot run (missing venv), state "metrics unavailable" in the report and
  continue with `Grep` / `Read`.

## 4. Rubric

Every finding carries a `file:line` location.

1. **Size / SRP** — oversized files and methods, classes with several responsibilities.
2. **Property vs methods** — argument-less `get_*` / `is_*` without side effects -> `@property`.
   `set_*` methods that contain logic stay methods.
3. **Testability** — I/O or `pygame.init` in constructors, logic glued to `Surface` / display.
4. **Duplication** — twin classes/files, repeated blocks.
5. **Idioms** — `list()` / `dict()` instead of `[]` / `{}`, dead code, missing type annotations
   on public API, redundant `else` after `return`.

## 5. Project rules for recommendations

- Cross-system communication only through Pygame custom events (`src/events.py:Events`).
- New modules only in `src/`, each with a test in `tests/` mirroring the module path.
- No new dependencies.
- Full, descriptive identifier names — no abbreviations or single-letter variables.
- Images are loaded through `SpriteHelper`, never `pygame.image.load` directly in UI classes.

## 6. Report format

Write the report in the user's language.

**Metrics (baseline)** — one table row per file in scope: SLOC, MI + rank, worst CC
(function + rank), number of ruff findings. Used for comparison on re-audit.

**Backlog** — items ranked by gain/risk. Each item:
- location (`file:line`),
- problem,
- metric evidence (e.g. `CC=18 (C)`, `PLR0912`) when available,
- minimal change,
- proposed characterization test (pins the current behavior before the refactor),
- risk — flag "Stop and Ask" when the change touches `GameManager` shared state or more
  than one rendering layer / `ObstacleMap`.

One item = one future commit. Do not bundle unrelated cleanups into one item.

## 7. Honesty

If a file has no design issues worth fixing, say so plainly. Do not invent items.
