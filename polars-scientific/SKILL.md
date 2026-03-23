---
name: polars-scientific
description: "Polars + NumPy for scientific and ML workflows. Covers selectors (cs), group_by_dynamic, Array columns for embeddings, NumPy-per-group patterns, join_nulls, explode+unpivot stacking, einops reshaping, and opinionated rules for research code."
---

# Polars for Scientific and ML Workflows

Use this skill when writing scientific or data analysis code using Polars alongside NumPy: any task involving DataFrames and numerical arrays, including grouping, joining, reshaping, or aggregating tabular data alongside NumPy computations.

## Rules

1. **Think like a database.** Research is often about comparing quantities across dimensions (layers, datasets, samples, hyperparameters). Build DataFrames, use joins and pivoting -- not nested loops or dicts.
2. **Stay in Polars expressions as long as possible.** Leave the engine only when NumPy or scipy is genuinely needed (linear algebra, signal processing, custom distance functions).
3. **Groups are for aggregation, not iteration.** Prefer `group_by().agg()` over any form of row-wise looping. When NumPy is required per group, collect into records with a list comprehension.
4. **Reshape tensors before creating DataFrames.** einops (`rearrange`, `repeat`) is the cleanest way to flatten high-dimensional arrays; plain NumPy reshaping also works.
5. **Give meaningful names to DataFrames.** Never overwrite a DataFrame. Each variable should describe its contents (e.g., `losses_with_grads`, not `df2`).

---

## Selectors: match columns by type or name pattern

You don't always need to name columns explicitly. `cs` selectors match by dtype, name pattern, or membership -- useful when schemas are wide or generated programmatically.

```python
import polars.selectors as cs

# Normalize all float columns at once
normalized = df.with_columns(
    (cs.float() - cs.float().mean()) / cs.float().std()
)

# Select metric columns by name pattern; exclude metadata columns
metrics = df.select(cs.starts_with("metric_") | cs.ends_with("_score"))
metadata_dropped = df.select(~cs.by_name("run_id", "timestamp"))

# In unpivot: pivot on all numeric columns, keep string columns as index
df.unpivot(on=cs.numeric(), index=cs.string())
```

---

## Examples

### Collect results into a tidy DataFrame

Research experiments often loop over hyperparameters. Wrap creation in a function with a descriptive name.

```python
import polars as pl
import numpy as np

def build_layer_accuracy_table(layers: list[int], datasets: list[str]) -> pl.DataFrame:
    rows = []
    for layer in layers:
        for dataset in datasets:
            rows.append({
                "layer": layer,
                "dataset": dataset,
                "accuracy": np.random.rand(),
            })
    return pl.DataFrame(rows)

layer_accuracies = build_layer_accuracy_table(
    layers=[0, 1, 2],
    datasets=["train", "test"],
)
```

### Join two measurements on shared keys

When you have two independent measurements (e.g., loss and gradient norms), join them on shared keys like SQL.

```python
losses = pl.DataFrame({
    "layer": [0, 1, 2, 0, 1, 2],
    "dataset": ["train", "train", "train", "test", "test", "test"],
    "loss": np.random.rand(6),
})

gradient_norms = pl.DataFrame({
    "layer": [0, 1, 2, 0, 1, 2],
    "dataset": ["train", "train", "train", "test", "test", "test"],
    "grad_norm": np.random.rand(6),
})

losses_with_grads = losses.join(gradient_norms, on=["layer", "dataset"])

loss_efficiency = losses_with_grads.with_columns(
    (pl.col("loss") / pl.col("grad_norm")).alias("loss_per_grad")
)
```

### Handling nulls and join_nulls

`fill_null` and `drop_nulls` handle the common cases. The less obvious one: by default Polars treats null as not equal to null on joins, so null-keyed rows are silently dropped. Pass `join_nulls=True` to match them explicitly.

```python
readings = pl.DataFrame({
    "sensor_id": [1, 2, None],
    "value": [10.0, 20.0, 30.0],
})

metadata = pl.DataFrame({
    "sensor_id": [1, None],
    "location": ["roof", "unknown"],
})

# null sensor_id correctly matches "unknown" location
readings_with_location = readings.join(metadata, on="sensor_id", how="left", join_nulls=True)
```

### Store vectors as Array columns

Polars infers Array type automatically for constant-length lists. This is the semantically correct way to store embeddings, feature vectors, and weight shapes. Array columns don't support most aggregation expressions -- use them for storage and retrieval, not computation. Access individual positions with `.arr.get(i)`.

```python
embeddings = np.random.randn(100, 64)

embeddings_df = pl.DataFrame({
    "sample_id": range(100),
    "embedding": list(embeddings),  # Polars infers Array(Float64, 64)
})

# Extract each position as its own column
# See: https://docs.pola.rs/api/python/stable/reference/series/array.html
positional_df = embeddings_df.select(
    "sample_id",
    *[pl.col("embedding").arr.get(i).alias(f"dim_{i}") for i in range(4)],
)
```

### Unpivot wide measurements into tidy format

When you have separate columns for each condition, unpivot to long format for grouping and plotting.

```python
layer_accuracies = pl.DataFrame({
    "layer": [0, 1, 2],
    "train_acc": [0.9, 0.85, 0.88],
    "test_acc": [0.8, 0.75, 0.78],
})

layer_accuracies_tidy = layer_accuracies.unpivot(
    on=["train_acc", "test_acc"],
    index="layer",
    variable_name="split",
    value_name="accuracy",
)
```

### Explode two array columns and tag their origin

When two array columns (e.g. original activations `A` and perturbed activations `A0`) have the same length per row, you often want to stack them into a single long column with a boolean flag indicating which source each value came from -- for instance, to compare distributions or plot them together. Explode both columns simultaneously to keep rows aligned, then `unpivot` to stack them, and finally turn the variable name into a boolean.

```python
samples = pl.DataFrame({
    "id": [0, 1],
    "A":  [[1.0, 2.0], [3.0, 4.0]],
    "A0": [[1.1, 2.2], [3.3, 4.4]],
})

stacked = (
    samples
    .explode(["A", "A0"])
    .unpivot(index="id", on=["A", "A0"], variable_name="from_A0", value_name="A")
    .with_columns(pl.col("from_A0") == "A0")
)
# +-----+------+---------+
# | id  | A    | from_A0 |
# | i64 | f64  | bool    |
# +=====+======+=========+
# | 0   | 1.0  | false   |
# | 0   | 1.1  | true    |
# | ... | ...  | ...     |
# +-----+------+---------+
```

### Unnest struct columns from aggregations

When you compute multiple stats per group using `pl.struct`, `unnest` flattens them into separate columns.

```python
group_stats = sample_data.group_by("group").agg(
    pl.struct(
        pl.col("x").mean().alias("mean_x"),
        pl.col("x").std().alias("std_x"),
        pl.col("y").mean().alias("mean_y"),
    ).alias("stats")
).unnest("stats")
```

### Apply a NumPy function per group

Stay in Polars expressions for standard aggregations. When you need NumPy -- correlations, decompositions, custom distances -- iterate with `group_by` directly, which yields `(key, sub_df)` tuples, and collect into records:

```python
correlations = pl.DataFrame([
    {"group": group_name, "correlation": np.corrcoef(sub_df["x"], sub_df["y"])[0, 1]}
    for (group_name,), sub_df in measurements.group_by("group")
])
```

> **Efficiency note.** The list comprehension approach exits the Polars execution engine -- each iteration crosses the Python boundary and converts columns to NumPy. This is fine for a small number of groups, but scales poorly. If you have hundreds of groups or large sub-DataFrames, consider whether the computation can be vectorized across the full arrays before grouping (e.g. pre-computing pairwise products, then aggregating), or batched using a compiled library.

### over and rank: first reading to exceed each sensor's personal best

`over` computes a window expression per group without collapsing rows (unlike `group_by`). Here it tracks each sensor's running maximum; `rank` then orders sensors within each building by how early they broke their record.

```python
sensor_readings = pl.DataFrame({
    "building": ["A", "A", "A", "A", "B", "B", "B", "B"],
    "sensor_id": [1, 1, 2, 2, 3, 3, 4, 4],
    "timestamp": [1, 2, 1, 2, 1, 2, 1, 2],
    "value": [10.0, 15.0, 12.0, 11.0, 8.0, 20.0, 14.0, 13.0],
})

# For each sensor, flag rows where value exceeds all previous readings
first_personal_bests = (
    sensor_readings
    .with_columns(
        pl.col("value")
          .shift(1)
          .cum_max()
          .over("sensor_id")
          .alias("prev_max")
    )
    .filter(pl.col("value") > pl.col("prev_max"))
    .group_by("sensor_id", "building")
    .agg(pl.col("timestamp").min().alias("first_pb_at"))
    .with_columns(
        pl.col("first_pb_at")
          .rank("ordinal")
          .over("building")
          .alias("rank_within_building")
    )
    .sort("building", "rank_within_building")
)
```

### Flatten a batch of features with einops

Use `rearrange` to flatten spatial dimensions before creating a DataFrame. Plain NumPy reshape works too (`array.reshape(8, -1)`), but einops makes the axis semantics explicit.

```python
from einops import rearrange, repeat

hidden_states = np.random.randn(8, 128, 256)  # (batch, seq_len, hidden_dim)

flat_hidden = rearrange(hidden_states, "b s d -> (b s) d")

token_df = pl.DataFrame({
    "sample_id": repeat(np.arange(8), "b -> (b s)", s=128),
    "position": repeat(np.arange(128), "s -> (b s)", b=8),
    "representation": list(flat_hidden),
})
```

### group_by_dynamic: time-based and index-based windows

[`group_by_dynamic`](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.group_by_dynamic.html) bins rows into fixed-width windows defined by a time or integer column, equivalent to pandas `resample`. The index column must be sorted. Windows are specified with a string interval language: `"1s"`, `"15m"`, `"1h"`, `"1d"`, `"1mo"`, `"3i"` (3 index steps), etc.

**Time-based:** aggregate sensor readings into 1-hour buckets, separately per sensor.

```python
from datetime import datetime

sensor_ts = pl.DataFrame({
    "sensor_id": ["A", "A", "A", "B", "B", "B"],
    "time": pl.datetime_range(
        datetime(2024, 1, 1), datetime(2024, 1, 1, 3), interval="1h", eager=True
    )[:6],
    "value": [1.0, 2.5, 3.1, 0.8, 1.4, 2.0],
})

# group_by is for categorical co-grouping alongside the time window
hourly_stats = sensor_ts.sort("time").group_by_dynamic(
    "time", every="1h", group_by="sensor_id"
).agg(
    pl.col("value").mean().alias("mean_value"),
    pl.col("value").count().alias("n_readings"),
)
```

**Index-based:** sliding windows over an ordered integer index -- useful for rolling baselines over fixed sample counts rather than calendar time.

```python
indexed_readings = pl.DataFrame({
    "idx": range(10),
    "value": np.random.randn(10),
})

# 3-sample windows starting every 2 samples
windowed = indexed_readings.group_by_dynamic(
    "idx", every="2i", period="3i"
).agg(
    pl.col("value").mean().alias("window_mean"),
)
```

---

## Reference

- [group_by API](https://docs.pola.rs/api/python/stable/reference/dataframe/group_by.html)
- [Array series methods](https://docs.pola.rs/api/python/stable/reference/series/array.html)
- [Series computation](https://docs.pola.rs/api/python/stable/reference/series/computation.html)
- [Series modify / select](https://docs.pola.rs/api/python/stable/reference/series/modify_select.html)

---

## Missing Polars features

Some common operations are not yet built into Polars expressions. Define them as standalone functions and call them inside `select` or `with_columns`.

### enumerate

Attach a row index to any column as a struct. Useful for ordered joins, ranking, and positional aggregations.

```python
def enumerate(expr: pl.Expr, name: str = "index") -> pl.Expr:
    return pl.struct(
        pl.int_range(pl.len()).alias(name),
        expr,
    ).alias(expr.meta.output_name())

df = pl.DataFrame({"num": [1, 2], "val": [["a", "c", "e"], ["b", "d", "f"]]})

df.select("num", enumerate(pl.col("val")))
# +-----+---------------------+
# | num | val                 |
# | i64 | struct[2]           |
# +=====+=====================+
# | 1   | {0,["a", "c", "e"]} |
# | 2   | {1,["b", "d", "f"]} |
# +-----+---------------------+

# To flatten to a tidy format:
df.select("num", enumerate(pl.col("val"))).unnest("val").explode("index", "val")
```
