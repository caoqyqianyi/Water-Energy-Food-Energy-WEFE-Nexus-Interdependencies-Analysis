"""Loading of spatial layers and pillar indicator tables."""

from pathlib import Path

import geopandas as gpd
import pandas as pd

from . import config


def try_load_csv(path):
    p = Path(path)
    if p.exists():
        # Add delimiter=';' to handle semicolon-separated files
        df = pd.read_csv(p, delimiter=';')
        print(f"Loaded {p.name} with shape {df.shape}")
        return df
    else:
        print(f"Skipping missing file: {p}")
        return None


def load_spatial_layers():
    """Load the analysis grid and the supporting polygon layers.

    Returns
    -------
    grid : GeoDataFrame
        Tunisia grid cells used as the common spatial unit.
    basins : GeoDataFrame
        Hydrological basin polygons (HydroBASINS level 4).
    climatic_zones : GeoDataFrame
        Climatic-zone polygons.
    """
    grid = gpd.read_file(config.GRID_PATH)
    basins = gpd.read_file(config.BASINS_PATH)
    climatic_zones = gpd.read_file(config.CLIMATIC_ZONES_PATH)
    return grid, basins, climatic_zones


def load_indicator_tables():
    """Load the pillar indicator tables and register them in a lookup dict.

    Attach a pointer so we can reference tables by name from metadata.
    """
    water_df = try_load_csv(config.WATER_CSV)
    energy_df = try_load_csv(config.ENERGY_CSV)
    food_df = try_load_csv(config.FOOD_CSV)

    tables = {
        'water': water_df,
        'energy': energy_df,
        'food': food_df,
    }
    return tables
