# Data inputs

The raw datasets are **not distributed** with this repository (they are large,
binary or licensed). Place them in this folder, or point the pipeline elsewhere
with the `WEFE_DATA_DIR` environment variable. The file names below match the
defaults in [`src/config.py`](../src/config.py).

## Spatial layers

| File | Description | Key columns |
|---|---|---|
| `TUN_cells_WGS84.shp` | Tunisia grid cells — the common spatial unit for every indicator (WGS84 / EPSG:4326) | `id`, `HYBAS_ID`, `clima_zone`, `pop_<year>`, `area_m2`, `pct_forest`, `pct_crop`, `geometry` |
| `TUN_WaterBasin_level04.shp` | Hydrological basins (HydroBASINS level 4) | `HYBAS_ID`, `geometry` |
| `TUN_ClimaticZone.shp` | Climatic-zone polygons | `clima_zone`, `geometry` |

The grid is the join target: it carries the basin identifier (`HYBAS_ID`) and
the climatic-zone identifier (`clima_zone`) so that basin- and zone-level
indicators can be attached without re-running spatial overlays.

## Indicator tables

Semicolon-separated (`;`) CSVs, one per pillar:

- `water_indicators.csv`
- `energy_indicators.csv`
- `food_indicators.csv`

Each table may contain:

- an optional **`data_year`** column for multi-year analysis (the pipeline
  selects the requested year and otherwise falls back to the latest available);
- one or more **value columns** whose names match the `value_col` entries in
  [`src/metadata.py`](../src/metadata.py);
- for basin / climatic-zone indicators, the corresponding identifier column
  (`HYBAS_ID`, `clima_zone`).

## Indicator metadata

`indicator_metadata.csv` is **generated automatically** on the first run from
`src/metadata.py`. Edit the metadata table (or the source) to add indicators,
change the assignment rule, flip the resilience direction, or introduce a new
pillar such as **Ecosystem**.

## Expected column reference (grid)

| Column | Meaning |
|---|---|
| `id` | Unique grid-cell identifier |
| `HYBAS_ID` | Hydrological basin identifier |
| `clima_zone` | Climatic-zone identifier |
| `pop_<year>` | Cell population for the analysis year |
| `area_m2` | Cell area in square metres |
| `pct_crop` | Share of cropland (0–1) |
| `pct_forest` | Share of forest / woody cover (0–1) |
