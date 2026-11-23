"""Print two conditional fossil-free electricity scenarios without writing files.

Fit annual changes to the 2020-2024 and 2015-2024 historical shares, then
extend each change from the observed 2024 share. These are not forecasts;
scenario lines stop when they reach the 100% boundary.
"""

from pathlib import Path
from statistics import linear_regression
import math

import pandas as pd

project_folder = Path(__file__).resolve().parent
input_file = (
    project_folder / "outputs" / "electricity_analysis_2015_2024.csv"
)

historical_data = pd.read_csv(input_file).sort_values("Year")

assert historical_data["Year"].tolist() == list(range(2015, 2025))
assert historical_data["Data_status"].eq("Historical").all()
assert historical_data["Fossil_free_share"].notna().all()
assert historical_data["Fossil_free_share"].between(0, 1).all()

base_year = 2024
base_share = historical_data.loc[
    historical_data["Year"].eq(base_year), "Fossil_free_share"
].item()

print(f"Both scenarios start at {base_year}: {base_share:.4%}")

for start_year in [2020, 2015]:
    period_data = historical_data.loc[
        historical_data["Year"].between(start_year, base_year)
    ]

    # Fit a straight line to all annual observations in this period.
    fitted_trend = linear_regression(
        period_data["Year"].tolist(),
        period_data["Fossil_free_share"].tolist(),
    )
    slope = fitted_trend.slope

    # Use the fitted slope, anchored to the observed 2024 share.
    scenario_2040 = base_share + slope * (2040 - base_year)

    print(f"\nPeriod: {start_year}-{base_year}")
    print(f"Annual observations: {len(period_data)}")
    print(f"Change: {slope * 100:.4f} percentage points per year")

    if slope > 0:
        crossing_year = base_year + (1 - base_share) / slope
        first_annual_year = math.ceil(crossing_year)

        print(f"Mathematical crossing: {crossing_year:.2f}")
        print(
            "First whole-year scenario point at or above 100%: "
            f"{first_annual_year}"
        )

        if crossing_year <= 2040:
            print("2040: the line reaches the 100% boundary before 2040.")
            print("Stop the scenario at that boundary; do not extend above it.")
        else:
            print(f"Conditional share in 2040: {scenario_2040:.4%}")
    else:
        print("No future 100% crossing under this non-increasing trend.")
        if 0 <= scenario_2040 <= 1:
            print(f"Conditional share in 2040: {scenario_2040:.4%}")
        else:
            print("The straight-line extension leaves the valid 0-100% range.")

print("\nCalculation complete. No CSV files were changed.")
