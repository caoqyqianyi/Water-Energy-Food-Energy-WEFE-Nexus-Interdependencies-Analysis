"""Spatial aggregation of pillar scores for the decision-support dashboard.

Rollups are produced at the national, climatic-zone and hydrological-basin
levels so that the Power BI / QGIS dashboard can be explored across scales.
"""

import pandas as pd

from .indicators import weighted_mean

# Choose weighting scheme for aggregations
# For population-weighted aggregation, use POP_COL
# For area-weighted, use 'area_m2'
# For crop/forest-specific, you can customize per indicator.

main_pillars = ['Water', 'Energy', 'Food']
pillar_score_cols = [f'{p}_score' for p in main_pillars]

def aggregate_scores(df, by=None, weight_col=None):
    # This list will now only contain the true pillar scores
    scores_to_aggregate = [c for c in pillar_score_cols if c in df.columns]

    if by is None:
        # national
        if weight_col and weight_col in df.columns:
            wt = df[weight_col]
            row = { 'level': 'national_weighted',
                    'WEFE_Nexus': weighted_mean(df['WEFE_Nexus'], wt) }
            for p in scores_to_aggregate:
                row[p] = weighted_mean(df[p], wt)
            return pd.DataFrame([row])
        else:
            row = { 'level': 'national_mean',
                    'WEFE_Nexus': df['WEFE_Nexus'].mean() }
            for p in scores_to_aggregate:
                row[p] = df[p].mean()
            return pd.DataFrame([row])
    else:
        grp = df.groupby(by)
        out = []
        for key, sub in grp:
            if weight_col and weight_col in sub.columns:
                wt = sub[weight_col]
                rec = { by: key, 'WEFE_Nexus': weighted_mean(sub['WEFE_Nexus'], wt) }
                for p in scores_to_aggregate:
                    rec[p] = weighted_mean(sub[p], wt)
            else:
                rec = { by: key, 'WEFE_Nexus': sub['WEFE_Nexus'].mean() }
                for p in scores_to_aggregate:
                    rec[p] = sub[p].mean()
            out.append(rec)
        return pd.DataFrame(out)


def build_aggregations(enriched, pop_col):
    """Build national, climatic-zone and basin rollups."""
    # National (population-weighted)
    agg_national = aggregate_scores(enriched, by=None, weight_col=pop_col)

    # By climatic zone (population-weighted)
    if 'climatic_zone_code' in enriched.columns:
        agg_zone = aggregate_scores(enriched, by='climatic_zone_code', weight_col=pop_col)
    else:
        agg_zone = pd.DataFrame()

    # By basin (population-weighted)
    if 'basin_id' in enriched.columns:
        agg_basin = aggregate_scores(enriched, by='basin_id', weight_col=pop_col)
    else:
        agg_basin = pd.DataFrame()

    return agg_national, agg_zone, agg_basin
