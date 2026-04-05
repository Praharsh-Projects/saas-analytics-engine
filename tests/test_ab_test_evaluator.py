import numpy as np
from statsmodels.stats.proportion import proportions_ztest

from analytics.ab_test_evaluator import ABTestEvaluator


def test_ab_test_pvalue_matches_statsmodels() -> None:
    control = np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 1], dtype=float)
    treatment = np.array([1, 1, 0, 1, 1, 0, 1, 1, 0, 1], dtype=float)

    evaluator = ABTestEvaluator(control, treatment)
    result = evaluator.evaluate()

    _, expected_p = proportions_ztest(
        count=np.array([control.sum(), treatment.sum()]),
        nobs=np.array([len(control), len(treatment)]),
        alternative="two-sided",
    )

    assert abs(result["p_value"] - float(expected_p)) < 1e-10
    assert "recommendation" in result
