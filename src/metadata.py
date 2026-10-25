"""Indicator metadata: pillar, spatial assignment, direction and source table.

Each row describes one indicator and tells the pipeline how it should be
allocated to the grid (population-weighted, national constant, basin level,
climatic-zone level or area-weighted) and whether a higher value represents
greater resilience (``pos``) or greater pressure (``neg``).

The framework is pillar-agnostic: adding a new pillar (e.g. "Ecosystem") is
simply a matter of adding rows here.
"""

from pathlib import Path

import pandas as pd

from . import config


def build_starter_metadata():
    """Return the starter indicator metadata table."""
    starter_meta = pd.DataFrame([
         # --- WATER ---
        # population-weighted national percentages (same % per cell; use pop for aggregations)
        dict(indicator='pct_basic_drinking_water', pillar='Water', assignment='population', direction='pos',
             table='water', value_col='pct_basic_drinking_water', zone_key='', basin_key='',
             notes='National %; per-cell percentage is constant; use population for weighted aggregation'),
        dict(indicator='pct_basic_sanitation', pillar='Water', assignment='population', direction='pos',
             table='water', value_col='pct_basic_sanitation', zone_key='', basin_key='',
             notes='National %; population-weighted for aggregations'),
        # basin-level (if water table has basin values; otherwise treated as national constant)
        dict(indicator='iwrm_implementation_score', pillar='Water', assignment='basin', direction='pos',
             table='water', value_col='iwrm_implementation_score', zone_key='', basin_key='HYBAS_ID',
             notes='If table lacks basin_id column, will fall back to national constant'),
        dict(indicator='annual_freshwater_withdrawals_pct', pillar='Water', assignment='national', direction='neg',
             table='water', value_col='annual_freshwater_withdrawals_pct', zone_key='', basin_key='',
             notes='National constant; higher is generally worse (pressure) → direction=neg'),
        dict(indicator='renewable_internal_freshwater_per_capita', pillar='Water', assignment='population', direction='pos',
             table='water', value_col='renewable_internal_freshwater_per_capita', zone_key='', basin_key='',
             notes='Per-capita national; use population for aggregations'),
        dict(indicator='environmental_flow_requirements_million_m3', pillar='Water', assignment='basin', direction='pos',
             table='water', value_col='environmental_flow_requirements_million_m3', zone_key='', basin_key='HYBAS_ID',
             notes='Assign per basin_id; same value to all basin cells'),
        dict(indicator='avg_precipitation_mm', pillar='Water', assignment='area', direction='pos',
             table='water', value_col='avg_precipitation_mm', zone_key='', basin_key='',
             notes='If provided as a single national/zonal figure, assigns constant; else supply zonal table'),

         # --- ENERGY --- (examples; edit as you have data)
        dict(indicator='access_to_electricity_pct', pillar='Energy', assignment='population', direction='pos',
             table='energy', value_col='access_to_electricity_pct', zone_key='', basin_key='',
             notes='Population-weighted national/subnational percentage'),
        dict(indicator='electric_power_consumption_kwh_per_capita', pillar='Energy', assignment='population', direction='pos',
             table='energy', value_col='electric_power_consumption_kwh_per_capita', zone_key='', basin_key='',
             notes='Per-capita; use population for aggregations'),
        dict(indicator='renewable_energy_consumption_pct', pillar='Energy', assignment='climatic_zone', direction='pos',
             table='energy', value_col='renewable_energy_consumption_pct', zone_key='clima_zone', basin_key='',
             notes='Assign per climatic zone or national'),
        dict(indicator='renewable_electricity_output_pct', pillar='Energy', assignment='national', direction='pos',
             table='energy', value_col='renewable_electricity_output_pct', zone_key='', basin_key='',
             notes='National constant'),
        dict(indicator='energy_imports_net_pct', pillar='Energy', assignment='national', direction='neg',
             table='energy', value_col='energy_imports_net_pct', zone_key='', basin_key='',
             notes='Macro-level pressure → direction=neg'),
        dict(indicator='co2_emissions_per_capita', pillar='Energy', assignment='population', direction='neg',
             table='energy', value_col='co2_emissions_per_capita', zone_key='', basin_key='',
             notes='Population-weighted; higher = worse → direction=neg'),

          # --- FOOD --- (examples; edit as you have data)
        dict(indicator='undernourishment_pct', pillar='Food', assignment='population', direction='neg',
             table='food', value_col='undernourishment_pct', zone_key='', basin_key='',
             notes='Higher is worse → direction=neg'),
        dict(indicator='avg_protein_supply_grams_per_capita_per_day', pillar='Food', assignment='population', direction='pos',
             table='food', value_col='avg_protein_supply_grams_per_capita_per_day', zone_key='', basin_key='',
             notes='Per-capita national'),
        dict(indicator='child_wasting_pct', pillar='Food', assignment='population', direction='neg',
             table='food', value_col='child_wasting_pct', zone_key='', basin_key='',
             notes='If subnational, add a zone_key column and values per zone'),
        dict(indicator='child_stunting_pct', pillar='Food', assignment='population', direction='neg',
             table='food', value_col='child_stunting_pct', zone_key='', basin_key='',
             notes='Same'),
        dict(indicator='adult_obesity_pct', pillar='Food', assignment='population', direction='neg',
             table='food', value_col='adult_obesity_pct', zone_key='', basin_key='',
             notes='Higher obesity = worse'),
        dict(indicator='adesa_pct', pillar='Food', assignment='national', direction='pos',
             table='food', value_col='adesa_pct', zone_key='', basin_key='',
             notes='National constant'),
        dict(indicator='avg_food_production_value_per_capita', pillar='Food', assignment='population', direction='pos',
             table='food', value_col='avg_food_production_value_per_capita', zone_key='', basin_key='',
             notes='Per-capita; population-weighted'),
        dict(indicator='cereal_yield_kg_per_hectare', pillar='Food', assignment='crop_area', direction='pos',
             table='food', value_col='cereal_yield_kg_per_hectare', zone_key='', basin_key='',
             notes='Area-weighted on cropland only via pct_crop'),

    ])
    return starter_meta


def load_metadata():
    """Write the starter metadata on first run, then read it from CSV."""
    starter_meta = build_starter_metadata()

    INDICATOR_META_CSV = config.INDICATOR_META_CSV
    meta_path = Path(INDICATOR_META_CSV)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    if not meta_path.exists():
        starter_meta.to_csv(meta_path, index=False)
        print(f"Starter metadata written to: {meta_path}")
    else:
        print(f"Using existing metadata at: {meta_path}")

    meta = pd.read_csv(meta_path)
    # The notebook used IPython's display(); print() is used here for the .py module.
    print(meta.head(12))
    return meta
