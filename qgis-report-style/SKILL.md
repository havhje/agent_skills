---
name: qgis-report-style
description: Apply the user's reusable QGIS map style to an existing QGIS project and produce a styled project or report-ready map. Use for consistent NDVI/terrain overlays, analysis boundaries, infrastructure emphasis, legends, and A3/A4 exports across projects; not for changing scientific calculations or source data.
---

# QGIS report style

Apply the visual system captured from
`/home/havhje/qgis-geoai/projects/sno_ugle.qgz`. Read the
[style specification](references/style-spec.md) before choosing assets or
changing a project.

Preserve the input project. Write a sibling `_styled.qgz` or another explicit
output path; do not overwrite source data, calculations, CRS, or the original
project. Treat layer-role matching as a semantic decision: ask or report an
ambiguity instead of applying a plausible-looking style to the wrong layer.

## Workflow

1. Inspect the project, visible extent, layer order, geometry types, raster
   bands, existing layouts, and broken sources.
2. Map relevant layers to roles. Use explicit `ROLE=LAYER_NAME` mappings when
   names are ambiguous.
3. Apply the matching QML assets with `scripts/apply_styles.py`, or use the QML
   files directly through PyQGIS. Keep continuous analysis rasters continuous.
4. Order overlays so infrastructure and boundaries are above the continuous
   surface-height layer, which is above NDVI and context layers.
5. Choose a QPT from `assets/layouts/`. For a standalone, portrait map plate,
   use `report-a4-portrait-page4.qpt`; set its map extent and the `map_date`,
   `prepared_by`, and `producer_name` layout variables. Its one-column legend
   updates from visible layers and is filtered by the linked map. Use the
   landscape templates when title, project, CRS, sources, or uncertainty text
   must appear on the map sheet. Remove irrelevant legend items.
6. Render a PNG preview with `scripts/render_project.py` and inspect it
   visually. Check legibility, source visibility, NoData, blending, labels,
   legend order, page margins, and whether the map communicates the intended
   variable hierarchy.
7. Return the styled QGZ and, when requested, PDF, PNG, and reusable QPT.

Run PyQGIS helpers through the packaged environment wrapper:

```bash
skill_dir=/home/havhje/.agents/skills/qgis-report-style
"$skill_dir/scripts/qgis-python" \
  "$skill_dir/scripts/apply_styles.py" input.qgz output_styled.qgz \
  --map ndvi-continuous=NDVI \
  --map surface-height=surface_height

"$skill_dir/scripts/qgis-python" \
  "$skill_dir/scripts/render_project.py" output_styled.qgz preview.png
```

The helper applies only unambiguous or explicit roles. It intentionally does
not invent scientific thresholds, hide inconvenient values, or turn an
exploratory blend into a habitat-probability map.
