from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm, ttest_ind
from statsmodels.stats.proportion import proportions_ztest


@dataclass
class ABTestResult:
    control_rate: float
    treatment_rate: float
    uplift: float
    p_value: float
    significant: bool
    confidence_interval: tuple[float, float]
    mde: float
    recommendation: str
    revenue_p_value: float | None = None


class ABTestEvaluator:
    def __init__(self, control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> None:
        self.control = np.asarray(control, dtype=float)
        self.treatment = np.asarray(treatment, dtype=float)
        self.alpha = alpha

    def _mde(self, pooled_rate: float, n_control: int, n_treatment: int) -> float:
        z_alpha = norm.ppf(1 - self.alpha / 2)
        z_beta = norm.ppf(0.8)
        pooled_se = np.sqrt(2 * pooled_rate * (1 - pooled_rate) * ((1 / n_control) + (1 / n_treatment)))
        return float((z_alpha + z_beta) * pooled_se)

    def evaluate(self, control_revenue: np.ndarray | None = None, treatment_revenue: np.ndarray | None = None) -> dict:
        n_control = len(self.control)
        n_treatment = len(self.treatment)

        if n_control == 0 or n_treatment == 0:
            raise ValueError("Control and treatment arrays must be non-empty.")

        control_converted = int(self.control.sum())
        treatment_converted = int(self.treatment.sum())

        stat, p_value = proportions_ztest(
            count=np.array([control_converted, treatment_converted]),
            nobs=np.array([n_control, n_treatment]),
            alternative="two-sided",
        )

        control_rate = control_converted / n_control
        treatment_rate = treatment_converted / n_treatment
        uplift = treatment_rate - control_rate

        pooled = (control_converted + treatment_converted) / (n_control + n_treatment)
        se = np.sqrt(pooled * (1 - pooled) * ((1 / n_control) + (1 / n_treatment)))
        z_critical = norm.ppf(1 - self.alpha / 2)
        ci_low = uplift - z_critical * se
        ci_high = uplift + z_critical * se

        mde = self._mde(pooled, n_control, n_treatment)
        significant = bool(p_value < self.alpha)

        if significant and uplift > 0:
            recommendation = "Ship treatment: statistically significant uplift detected."
        elif significant and uplift < 0:
            recommendation = "Do not ship: treatment significantly underperforms control."
        else:
            recommendation = "No significant effect: continue test or increase sample size."

        revenue_p_value = None
        if control_revenue is not None and treatment_revenue is not None:
            _, revenue_p_value = ttest_ind(
                np.asarray(control_revenue, dtype=float),
                np.asarray(treatment_revenue, dtype=float),
                equal_var=False,
                nan_policy="omit",
            )

        result = ABTestResult(
            control_rate=float(control_rate),
            treatment_rate=float(treatment_rate),
            uplift=float(uplift),
            p_value=float(p_value),
            significant=significant,
            confidence_interval=(float(ci_low), float(ci_high)),
            mde=float(mde),
            recommendation=recommendation,
            revenue_p_value=float(revenue_p_value) if revenue_p_value is not None else None,
        )
        return result.__dict__
