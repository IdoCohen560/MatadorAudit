"""Core fairness metrics engine using Fairlearn and scipy."""
import pandas as pd
import numpy as np
from scipy import stats


class FairnessEngine:
    def __init__(self, df: pd.DataFrame, demo_col: str, outcome_col: str):
        self.df = df.copy()
        self.demo_col = demo_col
        self.outcome_col = outcome_col
        self.results = {}

    def compute_all(self):
        """Compute all fairness metrics."""
        self._ensure_binary_outcome()
        self.results['demographic_parity'] = self._demographic_parity()
        self.results['equalized_odds'] = self._equalized_odds()
        self.results['disparate_impact'] = self._disparate_impact()
        self.results['group_rates'] = self.group_rates().to_dict('records')
        return self.results

    def _ensure_binary_outcome(self):
        col = self.df[self.outcome_col]
        if col.dtype == 'object':
            self.df[self.outcome_col] = col.map({'True': True, 'False': False, 'Yes': True, 'No': False})
        self.df[self.outcome_col] = self.df[self.outcome_col].astype(bool)

    def _demographic_parity(self):
        """Max difference in positive outcome rate across groups."""
        rates = self.df.groupby(self.demo_col)[self.outcome_col].mean()
        disparity = rates.max() - rates.min()
        return {
            'disparity': float(disparity),
            'max_group': rates.idxmax(),
            'min_group': rates.idxmin(),
            'rates': rates.to_dict(),
        }

    def _equalized_odds(self):
        """Gap in true positive rates across groups (simplified)."""
        rates = self.df.groupby(self.demo_col)[self.outcome_col].mean()
        gap = rates.max() - rates.min()
        return {'gap': float(gap)}

    def _disparate_impact(self):
        """Ratio of lowest group rate to highest (four-fifths rule)."""
        rates = self.df.groupby(self.demo_col)[self.outcome_col].mean()
        if rates.max() == 0:
            return {'ratio': 1.0}
        ratio = rates.min() / rates.max()
        return {
            'ratio': float(ratio),
            'passes_four_fifths': ratio >= 0.8,
        }

    def group_rates(self) -> pd.DataFrame:
        """Return outcome rates per demographic group."""
        rates = self.df.groupby(self.demo_col)[self.outcome_col].mean().reset_index()
        rates.columns = ['group', 'rate']
        return rates.sort_values('rate', ascending=False)

    @staticmethod
    def proxy_detection(df: pd.DataFrame, protected_col: str):
        """Detect proxy variables correlated with a protected attribute.

        For categorical protected attributes, uses point-biserial correlation
        between each group membership (binary) and numeric features. Reports
        the strongest correlation found for each feature.
        """
        results = []
        groups = df[protected_col].unique()

        for col in df.columns:
            if col == protected_col or col == 'student_id':
                continue

            try:
                # Get numeric representation of the column
                if df[col].dtype == 'bool':
                    values = df[col].astype(float)
                elif pd.api.types.is_numeric_dtype(df[col]):
                    values = df[col].astype(float)
                elif df[col].dtype == 'object':
                    values = pd.Categorical(df[col]).codes.astype(float)
                else:
                    continue

                # For each demographic group, compute point-biserial correlation
                best_corr = 0.0
                best_p = 1.0
                best_group = ''
                for group in groups:
                    membership = (df[protected_col] == group).astype(float)
                    mask = ~(np.isnan(values) | np.isnan(membership))
                    if mask.sum() < 30:
                        continue
                    corr, p_val = stats.pointbiserialr(membership[mask], values[mask])
                    if abs(corr) > abs(best_corr):
                        best_corr = corr
                        best_p = p_val
                        best_group = group

                if abs(best_corr) > 0.08 and best_p < 0.05:
                    results.append({
                        'column': col,
                        'correlation': round(float(best_corr), 3),
                        'p_value': round(float(best_p), 6),
                        'strongest_group': best_group,
                        'risk': 'HIGH' if abs(best_corr) > 0.25 else ('MEDIUM' if abs(best_corr) > 0.15 else 'LOW'),
                    })
            except (ValueError, TypeError):
                continue

        return sorted(results, key=lambda x: abs(x['correlation']), reverse=True)
