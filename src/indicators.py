"""Core indicator helpers: spatial assignment, normalization, weighting."""

import numpy as np
import pandas as pd


def assign_indicator_to_grid(grid_df, tables, meta_row, year, pop_col):
    """Assign one indicator to the grid based on metadata rules."""
    indicator = meta_row['indicator']
    value_col = meta_row['value_col']
    table_key  = str(meta_row['table']).lower() if pd.notna(meta_row['table']) else ''
    assignment = meta_row['assignment']
    zone_key   = meta_row['zone_key'] if pd.notna(meta_row['zone_key']) else ''
    basin_key  = meta_row['basin_key'] if pd.notna(meta_row['basin_key']) else ''

    df = tables.get(table_key)
    if df is None:
        # If no table, create a NaN column
        grid_df[indicator] = np.nan
        return grid_df

    row = pick_year_row(df, year)
    # For national constants or single-row tables, row may have only value columns

    g = grid_df.copy()

    if assignment == 'population':
        # Assign the same % or value to each cell; keep a helper 'weighted' column for aggregations
        val = row[value_col].iloc[0]
        g[indicator] = val
        # Optional: a people-based count for aggregations
        if pop_col in g.columns:
            g[indicator + "_people_equiv"] = g[pop_col] * (val / 100.0 if val > 1 else val)
        return g

    elif assignment == 'national':
        # Single national constant to all cells
        val = row[value_col].iloc[0]
        g[indicator] = val
        return g

    elif assignment == 'basin':
        # Expect a table with basin values (column matching grid 'HYBAS_ID' or meta basin_key)
        key = basin_key if basin_key else 'HYBAS_ID'
        if key not in g.columns:
            # Updated to use the correct key in the error message
            raise ValueError(f"Grid missing '{key}' for basin assignment.")
        # If the table doesn't have basin ids, treat as national constant
        possible_keys = [key, 'HYBAS_ID', 'basin_id', 'basin', 'basin_code']
        match_key = next((k for k in possible_keys if k in row.columns), None)
        if match_key is None:
            # No basin column present in the table
            val = row[value_col].iloc[0]
            g[indicator] = val
            return g
        tmp = row[[match_key, value_col]].drop_duplicates()
        g = g.merge(tmp, left_on=key, right_on=match_key, how='left')
        g[indicator] = g[value_col]
        g = g.drop(columns=[value_col, match_key])
        return g

    elif assignment == 'climatic_zone':
        key = zone_key if zone_key else 'clima_zone'
        if key not in g.columns:
            # Updated to use the correct key in the error message
            raise ValueError(f"Grid missing '{key}' for zone assignment.")
        possible_keys = [key, 'clima_zone', 'zone_id', 'climatic_zone_code', 'zone']
        match_key = next((k for k in possible_keys if k in row.columns), None)
        if match_key is None:
            # No zone column present in the table → treat as national constant
            val = row[value_col].iloc[0]
            g[indicator] = val
            return g
        tmp = row[[match_key, value_col]].drop_duplicates()
        g = g.merge(tmp, left_on=key, right_on=match_key, how='left')
        g[indicator] = g[value_col]
        g = g.drop(columns=[value_col, match_key])
        return g

    elif assignment in ('area','crop_area','forest_area','sum'):
        # These assume the value is already provided at grid or is a single national value.
        # If it's a single national/scalar, copy it to all; otherwise, if the column exists on the grid, use it.
        val = row[value_col].iloc[0]
        g[indicator] = val
        # If using crop/forest area weighting in aggregation, we will use pct_crop / pct_forest as weights later
        return g

    else:
        # Fallback: copy constant
        val = row[value_col].iloc[0]
        g[indicator] = val
        return g

def minmax_normalize(series, direction='pos'):
    s = series.astype(float)
    if s.notna().sum() <= 1:
        # Not enough variation; return 0.5 for non-null, else NaN
        return s.where(s.isna(), 0.5)
    s_min, s_max = s.min(), s.max()
    if s_max == s_min:
        norm = pd.Series(0.5, index=s.index)
    else:
        norm = (s - s_min) / (s_max - s_min)
    if str(direction).lower() == 'neg':
        norm = 1 - norm
    return norm

def weighted_mean(series, weights):
    w = weights.fillna(0).astype(float)
    s = series.astype(float)
    denom = w.sum()
    if denom == 0:
        return np.nan
    return (s * w).sum() / denom


def pick_year_row(df, year):
    if df is None:
        return None
    if 'data_year' not in df.columns:
        # assume a single-row table of constants
        return df.iloc[[0]]
    sel = df[df['data_year'] == year]
    if sel.empty:
        # fallback to latest available
        sel = df.sort_values('data_year').iloc[[-1]]
        print(f" Using latest available year {int(sel['data_year'].iloc[0])} for a table.")
    return sel

def safe_merge(left, right, left_key, right_key, how='left'):
    if right is None or right.empty:
        return left.copy()
    return left.merge(right[[right_key] + [c for c in right.columns if c not in ['data_year']]],
                      left_on=left_key, right_on=right_key, how=how)
