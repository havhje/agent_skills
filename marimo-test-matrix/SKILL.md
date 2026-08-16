---
name: marimo-test-matrix
description: Guides spec-first testing for data science code in marimo notebooks. Use when writing tests for DataFrame transformations, feature engineering, model or pipeline checks, expected input/output examples, source-of-truth matrices, or when preventing AI-generated tests from matching broken implementation behavior.
disable-model-invocation: true
---

# Marimo Test Matrix

Use this workflow when adding or revising tests for data science code in a marimo notebook.

## Core Rule

The current implementation is not the source of truth. Tests must come from an approved spec, hand-computed examples, data contracts, invariants, domain rules, or independent reference behavior.

Never write or update tests to match current broken output unless the user explicitly changes the approved matrix.

## Workflow

1. Inspect the target function, docstring, nearby markdown, existing tests, and project conventions.
2. Identify the test oracle:
   - hand-computed tiny examples
   - schema or data contract
   - documented domain rule
   - invariant/property
   - frozen labeled fixture
   - independent reference implementation
3. Draft the matrix in chat first when practical, especially before changing a notebook. If the user wants the matrix placed in the notebook immediately, create a visible markdown matrix cell near the function.
4. Stop and ask the user to approve or correct the matrix.
5. After approval, insert or update the notebook matrix cell and write executable test cells from the matrix.
6. If tests fail, fix code by default. Change tests only after the matrix changes.

If expected behavior is missing, ask targeted questions before writing tests. Do not infer expected outputs from the implementation.
Skip the approval stop only when the user has already explicitly approved a concrete matrix for the current task.
After approval, update the matrix approval status and preserve the approved behavior unless the user explicitly approves a revision.

## Matrix Cell Template

Create a visible marimo markdown cell like this and adapt the columns to the function:

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Test matrix: `function_name`

    **Intended behavior:** ...

    **Source of truth:** ...

    **Input contract:** required columns, dtypes, valid ranges/categories, null policy.

    **Output contract:** returned type, columns, dtypes, row-count policy, ordering policy.

    **Approval status:** Not approved yet. After approval, update to: Approved by user on YYYY-MM-DD.

    **Revision policy:** If expected behavior changes, update and re-approve this matrix before changing tests.

    | ID | Scenario | Input | Expected output/invariant | Tolerance | Why it matters | Failure mode guarded against | Test cell |
    |---|---|---|---|---|---|---|---|
    | MTM-001 | Happy path | ... | ... | ... | ... | ... | ... |
    | MTM-002 | Edge case | ... | ... | ... | ... | ... | ... |
    """)
    return
```

Use the user's language for notebook-facing markdown. Keep the matrix concrete enough that another agent can implement the tests without deciding expected behavior.
Give each row a stable ID such as `MTM-001` and reference that ID in the corresponding executable test cell so matrix coverage is traceable.

## What To Test

Prefer small, explicit fixtures that a human can inspect.

For DataFrame transformations, cover column names, dtypes, nulls, duplicates, boundary values, category mappings, ordering, row-count changes, and aggregation totals. Include contract and error cases such as missing required columns, wrong dtypes, invalid category values, duplicate keys, empty inputs, null-policy violations, and expected exceptions or error messages.

Use the dataframe library's assertion helpers when comparing full frames, such as `pandas.testing` or `polars.testing`.

For numeric code, use tolerances, shape checks, monotonicity/range invariants, and deterministic random seeds.

For feature engineering, test leakage risks, category encodings, missing/unknown categories, and reconciliation back to source totals.

For external data/API steps, use fakes or mocks. Do not make live network calls in tests unless the user explicitly requests an integration test.

For models and pipelines, prefer baseline comparisons, metric thresholds, slice checks, reproducibility checks, and schema validation over exact model outputs.

## Marimo Test Cells

Tests in marimo must actually execute.

Good patterns:
- direct assertions in a cell
- `check_*` helper functions called immediately in the same cell
- small fixture builders returned from one cell and consumed by a test cell

Avoid defining `test_*` functions that are never called. They look like pytest tests but do not execute automatically inside a notebook.

Reactivity checklist:
- Test cells should depend directly on the function under test and the fixtures they validate so marimo reruns them when code changes.
- After editing code or tests, rerun the affected cells or notebook and confirm assertions execute.
- Keep matrix row IDs visible in assertion messages, comments, or helper names.

Example:

```python
@app.cell
def _(function_name, pl):
    # MTM-001: nulls are filled without dropping rows
    source = pl.DataFrame({"x": [1, None, 3]})
    result = function_name(source)

    assert result.height == 3, "MTM-001 row count changed"
    assert result.get_column("x").null_count() == 0, "MTM-001 nulls remain"
    return
```

## Optional Pytest Promotion

Keep notebook tests close to the function while exploring. When a test becomes an important regression check, mirror the approved scenario into the project's normal pytest suite if one exists.

Pytest promotion should preserve the approved matrix behavior and use deterministic fixtures, fakes, and explicit assertions.

## Guardrails For AI-Written Tests

- Write the matrix before test code.
- Mark unknown expected behavior as "needs user decision".
- Include at least one test that would fail for the known bug when a known bug exists.
- Prefer exact expected outputs for tiny examples.
- Prefer invariants only when exact output is too brittle or not meaningful.
- Preserve failing tests that reveal implementation bugs.
- If tests fail, do not weaken expected outputs, broaden tolerances, reduce row coverage, or delete edge cases just to make tests pass unless the approved matrix changes.
