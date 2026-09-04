# QGIS report style specification

## Provenance

The canvas system was captured from
`/home/havhje/qgis-geoai/projects/sno_ugle.qgz`, saved with QGIS 3.44.7 on
2026-09-03. The reference project has no print layout. The packaged A3/A4
templates come from the earlier report-map system in
`/home/havhje/koding/snougle_habitat_finnmark/report_maps/`.

## Visual hierarchy

Use this order from top to bottom when the roles exist:

1. Infrastructure or impact features
2. Labels and analysis boundary
3. Surface-height or relief shading
4. Primary thematic raster such as NDVI
5. Muted topographic or satellite context

Do not make every layer equally prominent. The thematic raster provides hue;
surface height provides structure or darkness; infrastructure uses one strong
accent; context stays quiet.

## Captured layer roles

| Role | Captured treatment |
|---|---|
| `ndvi-continuous` | Single-band pseudocolor, linearly interpolated Viridis, display range 0.30–1.00, full opacity |
| `surface-height` | Single-band gray, white at 0 m and black at 2 m, stretch to min/max, 60% renderer opacity, Multiply blend mode |
| `wind-power` | Polygon outline only, red `#e41a1c`, solid 0.96 mm line, no fill |
| `study-boundary` | Restrained polygon boundary style captured from `east_of_alta` |
| `habitat-class` | Embedded screening-class palette and labels |
| `ndvi-class` | Embedded NDVI-class palette and labels |
| `height-class` | Embedded surface-height-class palette and labels |

The NDVI display range is symbology, not data filtering. Preserve original
pixel values. Surface height is DOM minus DTM and must be described as an
exploratory proxy when that is the input.

## Report page system

- Landscape A3 by default; A4 for short reports.
- Warm off-white paper `#f7f6f2`, ink `#202a33`, muted text `#5d6871`, rules
  `#7a858d`, teal accent `#195b6e`.
- Noto Sans, compact hierarchy, uppercase section labels.
- Dominant map frame with restrained UTM ticks, scale bar, north arrow, and a
  small locator map when it adds orientation.
- Bottom information band: legend on the left; map number, title, subtitle,
  project, producer, date, CRS, sources, and uncertainty on the right.
- Legends show only visible, decision-relevant layers and use plain-language
  units and thresholds.
- Do not copy consultancy logos or branding. The style is inspired by
  professional Norwegian impact-assessment cartography, not a replica.

### A4 portrait map plate

`assets/layouts/report-a4-portrait-page4.qpt` reproduces the map-only plate
embedded on page 4 of the Sortland nature-assessment reference. It does not
include the report header, figure caption, revision, or page footer.

- A4 portrait, white paper, with an approximately 3 mm outer margin.
- The framed map occupies the upper 244.5 mm. A 46.5 mm information band below
  it has a full-width heading row, a wide one-column legend, and a narrow
  metadata column.
- The legend is automatic, one column, filtered by the linked map, and limited
  to visible layers. Give layers concise report-facing names; use a manual
  legend label override only when renaming the project layer is inappropriate.
- The scale bar defaults to four 25 m segments to match the reference. Change
  units per segment for a different map scale while preserving its footprint.
- Set the layout variables `map_date`, `prepared_by`, and `producer_name`.
  An empty `map_date` uses the export date. `producer_name` is a neutral text
  placeholder, not a copied consultancy wordmark.
- The requested typeface is Arial. QGIS may substitute Liberation Sans where
  Arial is unavailable, so install an appropriately licensed Arial font when
  exact font metrics are required.
- After loading the template into another project, set the `map` item's extent
  from the intended canvas before checking the scale bar and legend.

## Adaptation rules

- Preserve a good existing extent unless the requested subject is clipped or
  excessively small.
- Use fixed thematic ranges when comparing maps in a series; use robust
  percentiles only for one-off exploration and report the chosen range.
- Keep NoData transparent.
- Prefer one accent colour plus a restrained scientific ramp.
- Preserve uncertainty and provenance in exported layouts.
- Do not expose sensitive species locations unless the user explicitly asks
  for them in the deliverable.
