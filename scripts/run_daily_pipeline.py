from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulate.generate_events import generate_saas_dataset
from analytics.generate_daily_report import build_daily_metrics_report


def main() -> None:
    generate_saas_dataset(n_users=5000, seed=42)
    build_daily_metrics_report()
    print("Daily pipeline completed")


if __name__ == "__main__":
    main()
