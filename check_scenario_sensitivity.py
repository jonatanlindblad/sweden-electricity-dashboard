"""Compare six historical trend periods without writing any files.

Extend each fitted slope from the same observed 2024 fossil-free share and
report the conditional outcome by 2040. The periods overlap and contain
different numbers of observations; these are not independent forecasts.
"""

from pathlib import Path
from statistics import linear_regression
import math

import pandas as pd


project_folder = Path(__file__).resolve().parent
input_file = project_folder / "outputs" / "electricity_analysis_2015_2024.csv"
historical_data = pd.read_csv(input_file).sort_values("Year")

assert historical_data["Year"].tolist() == list(range(2015, 2025)), "Check historical years."
assert historical_data["Data_status"].eq("Historical").all(), "Historical data only."
assert historical_data["Fossil_free_share"].notna().all(), "Missing share."
assert historical_data["Fossil_free_share"].between(0, 1).all(), "Share outside 0-100%."

base_year = 2024
horizon_year = 2040
base_share = historical_data.loc[
    historical_data["Year"].eq(base_year), "Fossil_free_share"
].item()
assert base_share < 1, "Review method: anchor already at the 100% boundary."

print("TREND-PERIOD SENSITIVITY: conditional scenarios, not forecasts")
print(f"Shared observed {base_year} anchor: {base_share:.4%}")
print("Fit all annual observations in each window; use only the fitted slope.")
print("Extend from the observed anchor, not from the fitted intercept.\n")
print(
    f"{'Trend period':<14} {'N':>2} {'Slope (pp/year)':>16} "
    f"{'100% crossing*':>15}  {'Outcome by 2040'}"
)

results = []
for start_year in range(2015, 2021):
    period_data = historical_data.loc[
        historical_data["Year"].between(start_year, base_year)
    ]
    assert len(period_data) == base_year - start_year + 1

    slope = linear_regression(
        period_data["Year"].tolist(), period_data["Fossil_free_share"].tolist()
    ).slope
    assert math.isfinite(slope)

    # Shares are fractions; multiply slope by 100 for percentage points/year.
    extension_2040 = base_share + slope * (horizon_year - base_year)
    crossing_year = base_year + (1 - base_share) / slope if slope > 0 else None
    reaches_boundary = crossing_year is not None and crossing_year <= horizon_year

    if reaches_boundary:
        # Stop at the boundary: do not present values above 100% or a plateau.
        outcome = "Reaches 100%; stop at boundary"
    elif 0 <= extension_2040 <= 1:
        outcome = f"{extension_2040:.4%}; short by {(1 - extension_2040) * 100:.4f} pp"
    else:
        outcome = "Extension leaves 0-100%; review lower boundary"

    crossing_label = f"{crossing_year:.2f}" if crossing_year is not None else "None"
    print(
        f"{start_year}-{base_year:<9} {len(period_data):>2} {slope * 100:>16.4f} "
        f"{crossing_label:>15}  {outcome}"
    )
    results.append((start_year, slope, reaches_boundary))

assert len(results) == 6
print("\n*Mathematical crossing under an unchanged slope, not a forecast date.")
print("pp = percentage points. N = number of annual observations.")
print("The windows overlap and contain different numbers of observations.")
print("This is sensitivity to period choice, not six independent forecasts.")
print("It does not establish the causes of change or prove sustained slowing.")
print("\nChecks passed: six complete windows; historical shares; common 2024 anchor.")
print("Calculation complete. No CSV files were created or changed.")
