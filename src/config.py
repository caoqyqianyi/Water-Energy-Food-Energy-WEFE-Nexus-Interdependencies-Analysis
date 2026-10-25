"""Configuration for the Tunisia WEFE Nexus climate-resilience pipeline.

The original Colab notebook read every input from a mounted Google Drive folder
(``/content/drive/MyDrive/TUN_wefe_PowerBI/``). For portability, all paths are
defined here and default to a local ``data/`` directory. The data location can
be overridden with the ``WEFE_DATA_DIR`` environment variable.
"""

import os
from pathlib import Path

# Base data directory (override with the WEFE_DATA_DIR environment variable).
DATA_DIR = Path(os.environ.get("WEFE_DATA_DIR", "data"))
OUTPUTS_DIR = DATA_DIR / "Outputs"

# --- Spatial layers ---
GRID_PATH = DATA_DIR / "TUN_cells_WGS84.shp"
BASINS_PATH = DATA_DIR / "TUN_WaterBasin_level04.shp"
CLIMATIC_ZONES_PATH = DATA_DIR / "TUN_ClimaticZone.shp"

# --- Pillar indicator tables (semicolon-separated CSVs) ---
WATER_CSV = DATA_DIR / "water_indicators.csv"
ENERGY_CSV = DATA_DIR / "energy_indicators.csv"
FOOD_CSV = DATA_DIR / "food_indicators.csv"

# --- Indicator metadata (auto-generated on first run) ---
INDICATOR_META_CSV = DATA_DIR / "indicator_metadata.csv"

# --- Analysis parameters ---
YEAR = 2019
POP_COL = f"pop_{YEAR}"


def ensure_dirs():
    """Create the output directory if it does not yet exist."""
    Path(OUTPUTS_DIR).mkdir(parents=True, exist_ok=True)
