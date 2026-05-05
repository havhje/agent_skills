---
name: marimo-pair-typed
disable-model-invocation: true
description: >-
  Pair-program in a running marimo notebook using marimo-live typed tools.
  Use for focused notebook context and rare marimo._code_mode fallbacks.
---

# marimo Pair Programming (Typed Tools)

This skill is a compact overlay on `marimo-live`. The extension already supplies
active tool schemas, connected guidance, autocomplete, and `@` mention context.
Avoid repeating tool docs or dumping notebook state.

## Core workflow

- Use focused `@` mentions for context.
- Use `marimo_run` for live inspection/prototypes; it does not persist cells.
- Use `marimo_list_cells` before editing; request full code only for selected ids.
- Use `marimo_cell` for persistent create/edit/delete/run changes.
- `marimo-live` auto-runs `marimo_check` once after dirty notebook edits; fix injected failures. Use `marimo_check` or `/marimo check` for an explicit pre-handoff check.
- Never edit the notebook `.py` file directly while connected.
- marimo is reactive: changing one cell can re-run downstream cells.

## Mentions and token control

Trust injected `marimo-mentioned-context` for mentioned objects, but do not assume
unmentioned notebook state.

Common forms:

```text
@df:schema                  # shape + schema/dtypes
@df:sample                  # bounded sample rows
@df:profile                 # schema + sample
@df:plan                    # lazy plan if available
@function:clean_data:source
@function:clean_data:signature
@cell:<id>:summary
@cell:<id>:code
@variable:config:value
@variable:model:repr
```

Prefer suffixes over broad context. Range suffixes like `@df:sample[30:60]` are
not supported; use `marimo_run` for targeted slices such as `cols[30:60]`.

## Advanced `code_mode` via `marimo_run`

Prefer typed tools first: `marimo_install_packages`, `marimo_set_ui_value`,
and `marimo_cell(action="run")` now cover common advanced operations.

Use private code-mode only for unsupported `ctx.*` operations:

```python
import marimo._code_mode as cm
async with cm.get_context() as ctx:
    print(dir(ctx))
```

Rules:

- Always use `async with cm.get_context() as ctx`.
- API shape may change; inspect before relying on a method.
- Prefer typed tools for run/list/cell/package/UI operations.

## Guard rails

- Install packages with `marimo_install_packages`, not `uv add`/`pip`, unless it fails and the user approves a fallback.
- The user may edit concurrently; re-inspect before risky edits.
- Deletes are destructive and remove variables from kernel memory; ask if unclear.
- Package installs modify the project; confirm if not obviously required.
- No temp-file dependencies in cells, e.g. `/tmp/...`.
- Use `marimo_set_ui_value` for `mo.ui`; use `marimo_run` for anywidget traitlets.
- Avoid empty cells; cell names are optional.

## Connecting

The extension may auto-connect when exactly one server/session exists. Otherwise
ask the user to run `/marimo`. If no server is running:

```bash
uv run marimo edit --no-token notebook.py
```

For token-authenticated servers, Pi needs `MARIMO_TOKEN`.

## References

- [finding-marimo.md](reference/finding-marimo.md)
- [gotchas.md](reference/gotchas.md)
- [rich-representations.md](reference/rich-representations.md)
- [notebook-improvements.md](reference/notebook-improvements.md)
