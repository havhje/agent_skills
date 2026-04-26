---
name: marimo-pair-typed
disable-model-invocation: true
description: >-
  Work inside a running marimo notebook's kernel using the marimo_run and
  marimo_cell tools. Execute code, create cells, and build a notebook as an
  artifact. Use when the user wants to work in an active marimo session.
---

# marimo Pair Programming (Typed Tools)

The user connects to a running notebook via `/marimo`. Once connected,
use the marimo tools directly — no scripts, no shell.

## Philosophy

marimo notebooks are a dataflow graph — cells are the fundamental unit of
computation, connected by the variables they define and reference. When a cell
runs, marimo automatically re-executes downstream cells.

- **Cells are your main lever.** Use them to break up work and choose how and
  when to bring the human into the loop. Not every cell needs rich output —
  sometimes the object itself is enough, sometimes a summary is better.
  Match the presentation to the intent.
- **Understand intent first.** When clear, act. When ambiguous, clarify.
- **Follow existing signal.** Check imports, `pyproject.toml`, existing cells,
  and `dir(ctx)` before reaching for external tools.
- **Stay focused.** Build first, polish later — cell names, layout, and styling
  can wait.

## Connecting

The extension auto-connects when exactly one server with one session is found.
Otherwise the user runs `/marimo` to pick. If no server is running, tell the
user to start one:

```bash
uv run marimo edit notebook.py --no-token
```

Only `--no-token` servers are auto-discoverable. For token auth, set
`MARIMO_TOKEN`. See [finding-marimo.md](reference/finding-marimo.md) for
the full decision tree.

## code_mode API (via marimo_run)

For operations beyond create/edit/delete, use `marimo_run` with the
`code_mode` API directly:

**Install packages:**
```
marimo_run: code="import marimo._code_mode as cm\nasync with cm.get_context() as ctx:\n    ctx.install_packages('pandas', 'seaborn')"
```

**Set UI element values:**
```
marimo_run: code="import marimo._code_mode as cm\nasync with cm.get_context() as ctx:\n    ctx.set_ui_value(slider, 5)"
```

**Explore the code_mode API (do this first — it can change between versions):**
```
marimo_run: code="import marimo._code_mode as cm\nasync with cm.get_context() as ctx:\n    print(dir(ctx))"
```

The `code_mode` API rules:
- You **must** use `async with` — without it, operations silently do nothing.
- All `ctx.*` methods are **synchronous** — they queue operations and the
  context manager flushes them on exit. Do **not** `await` them.
- `create_cell` and `edit_cell` are structural only — use `run_cell` to
  execute. (`marimo_cell` handles this automatically.)

## Guard Rails

Skip these and the UI breaks:

- **Install packages via `ctx.install_packages()`, not `uv add` or `pip`.**
  Only fall back to external CLIs if the API fails.
- **Custom widget = anywidget.** `mo.ui` is fine for simple controls.
  See [rich-representations.md](reference/rich-representations.md).
- **NEVER write to the `.py` file directly — the kernel owns it.**
- **No temp-file deps in cells.** `pathlib.Path("/tmp/...")` is a bug.
- **Avoid empty cells.** Edit existing empty cells rather than creating new ones.
- **Cell names are optional.** Most don't need them —
  see [notebook-improvements.md](reference/notebook-improvements.md#cell-names).
- **Anywidget reactivity:** bridge traits with `mo.state` + `.observe()`
  (default) or `mo.ui.anywidget()` (coarser). One strategy per widget.
  See [rich-representations.md](reference/rich-representations.md).

## Keep in Mind

- **The user is editing too.** The notebook can change between your calls —
  re-inspect notebook state if it's been a while since you last looked.
- **Deletions are destructive.** Deleting a cell removes its variables from
  kernel memory — restoring means recreating the cell and re-running it and
  its dependents. If intent seems ambiguous, ask first.
- **Installing packages changes the project.** `ctx.install_packages()` adds
  real dependencies — confirm when it's not obvious from context.

## References

- [finding-marimo.md](reference/finding-marimo.md) — how to find and invoke the right marimo
- [gotchas.md](reference/gotchas.md) — cached module proxies and other traps
- [rich-representations.md](reference/rich-representations.md) — custom widgets and visualizations
- [notebook-improvements.md](reference/notebook-improvements.md) — improving existing notebooks
