"""Prepare historical shares and two conditional scenario lines for Power BI.

Start both scenarios at the observed 2024 share and extend their fitted annual
changes until 2040 or the 100% boundary, whichever comes first. Export the
chart points with source and point descriptions; the scenarios are not forecasts.
"""

from pathlib import Path
from statistics import linear_regression

import pandas as pd

project_folder = Path(__file__).resolve().parent
output_folder = project_folder / "outputs"

historical_data = pd.read_csv(
    output_folder / "electricity_analysis_2015_2024.csv"
).sort_values("Year")

assert historical_data["Year"].tolist() == list(range(2015, 2025))
assert historical_data["Data_status"].eq("Historical").all()
assert historical_data["Fossil_free_share"].notna().all()
assert historical_data["Fossil_free_share"].between(0, 1).all()

base_year = 2024
base_share = historical_data.loc[
    historical_data["Year"].eq(base_year), "Fossil_free_share"
].item()

records = []

# Historical observations: 2015–2024 only.
for row in historical_data.itertuples(index=False):
    records.append({
        "Year": float(row.Year),
        "Series": "Historical",
        "Share": row.Fossil_free_share,
        "Point_type": "Historical observation",
    })

# Conditional scenarios, anchored to the observed 2024 share.
for start_year in [2020, 2015]:
    period_data = historical_data.loc[
        historical_data["Year"].between(start_year, base_year)
    ]

    slope = linear_regression(
        period_data["Year"].tolist(),
        period_data["Fossil_free_share"].tolist(),
    ).slope

    # These two verified windows currently have positive slopes.
    assert slope > 0, "Trend changed; review the scenario before exporting."

    crossing_year = base_year + (1 - base_share) / slope
    end_year = min(2040.0, crossing_year)

    # Annual points followed by the exact endpoint.
    years = [
        float(year)
        for year in range(base_year, 2041)
        if year < end_year
    ]
    years.append(end_year)

    for year in years:
        at_boundary = (
            crossing_year <= 2040 and year == end_year
        )

        share = (
            1.0 if at_boundary
            else base_share + slope * (year - base_year)
        )

        if year == base_year:
            point_type = "Anchor: observed 2024 value"
        elif at_boundary:
            point_type = "Mathematical boundary, not a forecast date"
        else:
            point_type = "Conditional scenario"

        records.append({
            "Year": year,
            "Series": f"Scenario: {start_year}-2024 trend",
            "Share": share,
            "Point_type": point_type,
        })

dashboard_trends = pd.DataFrame(records)
dashboard_trends = dashboard_trends.sort_values(["Series", "Year"]).reset_index(drop=True)

dashboard_trends["Source"] = (
    "Energimyndigheten, Energiindikatorer i siffror 2026, sheet 6.1; "
    "scenario values calculated from historical shares."
)

assert not dashboard_trends.duplicated(["Year", "Series"]).any()
assert dashboard_trends["Share"].between(0, 1).all()

anchors = dashboard_trends.loc[dashboard_trends["Year"].eq(2024), "Share"]
assert len(anchors) == 3
assert (anchors - base_share).abs().lt(0.000001).all()

output_file = output_folder / "dashboard_fossil_free_trends.csv"
dashboard_trends.to_csv(output_file, index=False, encoding="utf-8-sig")

saved = pd.read_csv(output_file)
assert len(saved) == 38
assert saved["Share"].between(0, 1).all()

print("Rows per series:")
print(saved.groupby("Series").size().to_string())

print("\nLast point in each series:")
for series, group in saved.groupby("Series"):
    last = group.sort_values("Year").iloc[-1]
    print(f"{series}: year {last['Year']:.2f}, share {last['Share']:.4%}")

print("\nChecks passed: 38 rows; shared 2024 anchor; no shares above 100%.")
print(f"Saved: {output_file}")
