"""Export six trend-period summaries for the Power BI sensitivity page.

Use a shared observed 2024 starting share and leave the 2040 share blank when
its scenario stops at the 100% boundary. Check the two existing chart endpoints
and preserve source references, method descriptions and limitations in the CSV.
"""

from pathlib import Path
from statistics import linear_regression
import math

import pandas as pd


project_folder = Path(__file__).resolve().parent
output_folder = project_folder / "outputs"
historical_data = pd.read_csv(output_folder / "electricity_analysis_2015_2024.csv")
historical_data = historical_data.sort_values("Year")

assert historical_data["Year"].tolist() == list(range(2015, 2025))
assert historical_data["Data_status"].eq("Historical").all()
assert historical_data["Fossil_free_share"].notna().all()
assert historical_data["Fossil_free_share"].between(0, 1).all()

base_year = 2024
horizon_year = 2040
base_share = historical_data.loc[historical_data["Year"].eq(base_year), "Fossil_free_share"].item()
assert base_share < 1, "Review method: anchor already at 100%."

records = []
for start_year in range(2015, 2021):
    period_data = historical_data.loc[historical_data["Year"].between(start_year, base_year)]
    assert len(period_data) == base_year - start_year + 1
    slope = linear_regression(
        period_data["Year"].tolist(), period_data["Fossil_free_share"].tolist()
    ).slope

    # All six checked windows have positive slopes. Stop for review if changed.
    assert math.isfinite(slope) and slope > 0, "Trend changed; review export."
    crossing_year = base_year + (1 - base_share) / slope
    reaches_boundary = crossing_year <= horizon_year
    extension_2040 = base_share + slope * (horizon_year - base_year)

    # A blank means the scenario stops at 100%, not missing source data.
    share_2040 = None if reaches_boundary else extension_2040
    outcome = (
        "Reaches 100% by 2040; stops at boundary"
        if reaches_boundary
        else f"Below 100% in 2040 ({share_2040:.2%})"
    )
    records.append({
        "Trend_period": f"{start_year}-{base_year}",
        "Start_year": start_year,
        "End_year": base_year,
        "Observations": len(period_data),
        "Slope_pp_per_year": slope * 100,
        "Anchor_year": base_year,
        "Anchor_share": base_share,
        "Mathematical_crossing_year": crossing_year,
        "Reaches_100_by_2040": "Yes" if reaches_boundary else "No",
        "Share_2040": share_2040,
        "Outcome_by_2040": outcome,
        "Source": "Energimyndigheten, Energiindikatorer i siffror 2026, sheet 6.1",
        "Method": (
            "Ordinary least-squares slope fitted to annual historical shares; "
            "extension anchored to observed 2024 share, not fitted intercept."
        ),
        "Notes": (
            "Conditional scenario, not forecast. Crossing year is mathematical. "
            "Overlapping windows of different lengths are not independent cases "
            "or probabilities. Share_2040 is blank when the line reaches 100% "
            "by 2040 and stops; no plateau or shares above 100% are assumed. "
            "Slope is percentage points/year; shares are fractions. "
            "Workbook 2024 share is about 98.65%; published 98.8% summary "
            "remains unreconciled."
        ),
    })

dashboard_sensitivity = pd.DataFrame(records)
assert dashboard_sensitivity["Start_year"].tolist() == list(range(2015, 2021))
assert dashboard_sensitivity["Observations"].tolist() == [10, 9, 8, 7, 6, 5]
assert dashboard_sensitivity["Trend_period"].is_unique
assert dashboard_sensitivity["Anchor_share"].eq(base_share).all()
assert dashboard_sensitivity["Share_2040"].dropna().between(0, 1).all()
assert dashboard_sensitivity["Share_2040"].isna().equals(dashboard_sensitivity["Reaches_100_by_2040"].eq("Yes"))

# Reconcile the two existing scenarios with their exported chart endpoints.
existing = pd.read_csv(output_folder / "dashboard_fossil_free_trends.csv")
for start_year in (2015, 2020):
    row = dashboard_sensitivity.loc[dashboard_sensitivity["Start_year"].eq(start_year)].iloc[0]
    series = existing.loc[existing["Series"].eq(f"Scenario: {start_year}-2024 trend")]
    assert not series.empty, "Existing scenario is missing."
    last = series.sort_values("Year").iloc[-1]
    end_year = min(horizon_year, row["Mathematical_crossing_year"])
    end_share = 1.0 if row["Reaches_100_by_2040"] == "Yes" else row["Share_2040"]
    assert math.isclose(last["Year"], end_year, rel_tol=0, abs_tol=1e-8)
    assert math.isclose(last["Share"], end_share, rel_tol=0, abs_tol=1e-12)

output_file = output_folder / "dashboard_sensitivity.csv"
dashboard_sensitivity.to_csv(output_file, index=False, encoding="utf-8-sig", na_rep="")
saved = pd.read_csv(output_file)
pd.testing.assert_frame_equal(dashboard_sensitivity, saved, check_exact=False, rtol=1e-12, atol=1e-12)

print(saved[[
    "Trend_period", "Observations", "Slope_pp_per_year",
    "Mathematical_crossing_year", "Outcome_by_2040",
]].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
print("\nChecks passed: 6 rows; 6 periods; common 2024 anchor.")
print("Existing 2015-2024 and 2020-2024 scenario endpoints reconciled.")
print(f"Intentional blank 2040 shares: {saved['Share_2040'].isna().sum()}.")
print("Slope_pp_per_year: decimal number, NOT percentage formatting.")
print("Anchor_share and Share_2040: fractions, suitable for percentage formatting.")
print(f"Saved: {output_file}")
