"""Prepare historical electricity-mix shares for the Power BI stacked chart.

Derive the fossil share from the indicator-workbook fossil-free share, then
export one row per year and category with source and method descriptions.
"""

from pathlib import Path

import pandas as pd

project_folder = Path(__file__).resolve().parent
output_folder = project_folder / "outputs"

historical_data = pd.read_csv(
    output_folder / "electricity_analysis_2015_2024.csv"
).sort_values("Year")

assert historical_data["Year"].tolist() == list(range(2015, 2025))
assert historical_data["Data_status"].eq("Historical").all()

# Derive the remaining share using only the indicator workbook.
historical_data["Fossil_share"] = 1 - historical_data["Fossil_free_share"]

share_columns = [
    "Renewable_share",
    "Nuclear_share",
    "Fossil_share",
]

assert historical_data[share_columns].notna().all().all()
assert historical_data[share_columns].ge(0).all().all()
assert historical_data[share_columns].le(1).all().all()

totals = historical_data[share_columns].sum(axis=1)
assert (totals - 1).abs().lt(0.000001).all()

# Keep the year and turn the three share columns into three rows per year.
# Power BI uses Category for the legend and Share for the bar sizes.
dashboard_mix = historical_data[["Year"] + share_columns].melt(
    id_vars="Year",
    var_name="Category",
    value_name="Share",
)

dashboard_mix["Category"] = dashboard_mix["Category"].replace({
    "Renewable_share": "Renewable",
    "Nuclear_share": "Nuclear",
    "Fossil_share": "Fossil",
})

dashboard_mix["Data_status"] = "Historical"
dashboard_mix["Source"] = "Energimyndigheten, Energiindikatorer i siffror 2026, sheet 6.1"
dashboard_mix["Method"] = "Share taken from indicator workbook."
dashboard_mix.loc[dashboard_mix["Category"].eq("Fossil"), "Method"] = (
    "Derived as 1 minus the workbook's fossil-free share."
)

dashboard_mix = dashboard_mix.sort_values(["Year", "Category"]).reset_index(drop=True)

assert len(dashboard_mix) == 30
assert not dashboard_mix.duplicated(["Year", "Category"]).any()

output_file = output_folder / "dashboard_historical_mix.csv"
dashboard_mix.to_csv(output_file, index=False, encoding="utf-8-sig")

# Check the saved file.
saved = pd.read_csv(output_file)
saved_totals = saved.groupby("Year")["Share"].sum()
assert (saved_totals - 1).abs().lt(0.000001).all()

preview = saved.loc[
    saved["Year"].eq(2024), ["Year", "Category", "Share"]
].copy()
preview["Share"] = preview["Share"].map(lambda value: f"{value:.4%}")

print(preview.to_string(index=False))
print("\nChecks passed: 30 rows; each year's shares total 100%.")
print(f"Saved: {output_file}")
