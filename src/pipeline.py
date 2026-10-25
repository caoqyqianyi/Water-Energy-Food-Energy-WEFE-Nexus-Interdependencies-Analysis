"""End-to-end WEFE Nexus climate-resilience indicator pipeline.

Reproduces the original notebook workflow:

    spatial layers + indicator tables
        -> grid assignment
        -> direction-aware normalization
        -> pillar scores & composite WEFE Nexus
        -> multi-scale aggregation
        -> export for Power BI / QGIS

Run with ``python main.py`` from the repository root.
"""

import os

import cartopy
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterio.mask

from . import config
from .aggregation import build_aggregations
from .data_loader import load_indicator_tables, load_spatial_layers
from .indicators import assign_indicator_to_grid, minmax_normalize
from .metadata import load_metadata

pd.set_option("display.max_columns", 200)


def run_pipeline(year=None):
    # 1. Load the grid cells of Tunisia and set the user inputs
    grid, basins, climatic_zones = load_spatial_layers()
    outputs = config.OUTPUTS_DIR
    if year is None:
        year = config.YEAR
    pop_col = f"pop_{year}"

    os.makedirs(outputs, exist_ok=True)
    print("Will write outputs to:", outputs)

    # 2. Water basin and climatic zone shapefiles are loaded above.
    # 3. Load the tabular data
    tables = load_indicator_tables()

    # 4. Define metadata for assignment
    meta = load_metadata()

    # 5. Prepare the grid cover weights
    enriched = grid.copy()

    # Ensure float % cover columns are in [0,1] for weighting convenience later
    for c in ['pct_crop','pct_forest']:
        if c in enriched.columns and enriched[c].max() > 1.0:
            # assume 0-100%
            enriched[c] = enriched[c] / 100.0

    # Apply assignments
    for _, row in meta.iterrows():
        ind = row['indicator']
        table_key = str(row['table']).lower()
        if table_key not in tables:
            print(f"Skipping {ind}: table '{table_key}' not among {list(tables.keys())}")
            continue
        enriched = assign_indicator_to_grid(enriched, tables, row, year, pop_col)

    print("Assigned indicators added to grid. Current columns:")
    print([c for c in enriched.columns if c not in grid.columns])

    # Normalize, Build Pillar Score, and WEFE Nexus
    # Group indicators by pillar from metadata
    pillar_to_inds = (meta.groupby('pillar')['indicator']
                        .apply(list)
                        .to_dict())

    # Normalize each indicator per its direction
    for _, row in meta.iterrows():
        ind = row['indicator']
        direction = row['direction']
        col = ind
        if col in enriched.columns:
            enriched[ind + "_norm"] = minmax_normalize(enriched[col], direction=direction)
        else:
            print(f"Missing indicator column for normalization: {ind}")

    # Compute pillar scores as simple mean of normalized indicators present
    for pillar, inds in pillar_to_inds.items():
        norm_cols = [f"{i}_norm" for i in inds if f"{i}_norm" in enriched.columns]
        if not norm_cols:
            enriched[pillar + "_score"] = np.nan
        else:
            enriched[pillar + "_score"] = enriched[norm_cols].mean(axis=1)

    # Correctly identify only the composite pillar scores
    pillar_scores = [f"{p}_score" for p in pillar_to_inds.keys()]
    # Filter out any pillar scores that didn't get a column
    pillar_scores = [p for p in pillar_scores if p in enriched.columns]
    enriched['WEFE_Nexus'] = enriched[pillar_scores].mean(axis=1)

    print("Pillar columns:", pillar_scores)

    # Aggregations for PowerBI (National, Climatic Zones, Basins)
    agg_national, agg_zone, agg_basin = build_aggregations(enriched, pop_col)

    # Export for PowerBI
    # Export enriched grid attributes as CSV (no geometry) for Power BI
    attr_cols = ['id','HYBAS_ID','clima_zone', pop_col, 'area_m2','pct_forest','pct_crop'] + [c for c in enriched.columns if c.endswith('_norm') or c.endswith('_score') or c == 'WEFE_Nexus'] + [c for c in enriched.columns if c in meta['indicator'].tolist()]

    attr_cols = [c for c in attr_cols if c in enriched.columns]  # keep only existing

    grid_attr = enriched[attr_cols].copy()
    grid_attr.to_csv(f"{outputs}/wefe_grid_attributes_{year}.csv", index=False)

    # Export rollups
    agg_national.to_csv(f"{outputs}/wefe_national_{year}.csv", index=False)
    if not agg_zone.empty:
        agg_zone.to_csv(f"{outputsR}/wefe_climatic_zone_{year}.csv", index=False)
    if not agg_basin.empty:
        agg_basin.to_csv(f"{outputs}/wefe_basin_{year}.csv", index=False)

    # Optional: Export geometry (GeoJSON) with id + scores (convert to TopoJSON via mapshaper.org)
    geo_cols = ['id','WEFE_Nexus'] + [c for c in enriched.columns if c.endswith('_score')]
    geo_cols = [c for c in geo_cols if c in enriched.columns]
    enriched_geo = enriched[geo_cols + ['geometry']].copy()
    out_geo = f"{outputs}/wefe_grid_{year}.geojson"
    enriched_geo.to_file(out_geo, driver='GeoJSON')

    print("✔ Exports written:")
    print("-", f"{outputs}/wefe_grid_attributes_{year}.csv")
    print("-", f"{outputs}/wefe_national_{year}.csv")
    if not agg_zone.empty:
        print("-", f"{outputs}/wefe_climatic_zone_{year}.csv")
    if not agg_basin.empty:
        print("-", f"{outputs}/wefe_basin_{year}.csv")
    print("-", out_geo, "(convert to TopoJSON for Power BI Shape Map)")

    return {
        'enriched': enriched,
        'agg_national': agg_national,
        'agg_zone': agg_zone,
        'agg_basin': agg_basin,
        'outputs': outputs,
    }
