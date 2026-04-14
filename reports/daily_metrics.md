# Daily SaaS Metrics Report

Generated: 2026-04-14 08:06 UTC

## Topline
- Users in dataset: **5,000**
- Events in dataset: **112,024**
- Experiments tracked: **1**

## Activation Funnel
- Biggest drop-off step: **teammate_invited** (71.8% drop-off)

| step                  |   users |   conversion_from_previous |   dropoff_from_previous |
|:----------------------|--------:|---------------------------:|------------------------:|
| signup                |    5000 |                   1        |                0        |
| onboarding_started    |    4113 |                   0.8226   |                0.1774   |
| onboarding_completed  |    2536 |                   0.616582 |                0.383418 |
| first_project_created |    1186 |                   0.467666 |                0.532334 |
| teammate_invited      |     335 |                   0.282462 |                0.717538 |

## A/B Test Evaluation
- Control conversion: **46.72%**
- Treatment conversion: **54.66%**
- Uplift: **7.95%**
- p-value: **0.0000**
- 95% CI: **[5.18%, 10.72%]**
- MDE (80% power): **5.60%**
- Recommendation: **Ship treatment: statistically significant uplift detected.**

## Cohort Retention
- Weekly cohort retention matrix generated.

## Artifacts
- `reports/funnel.png`
- `reports/cohort_heatmap.png`