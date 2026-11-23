"""Prepare a checked table of historical electricity shares for 2015-2024.

Read sheet 6.1 without changing the source workbook. Save the shares, source
references and limitations to CSV, leaving unverified production values blank.
"""

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

project_folder = Path(__file__).resolve().parent
source_file = (
    project_folder / "research" / "2026-10-20" / "indicators.xlsx"
)

workbook = load_workbook(
    source_file,
    read_only=True,
    data_only=True,
)
sheet = workbook["6.1"]

records = []

# I–R: historical years 2024 back to 2015.
for excel_column in range(9, 19):
    year = int(sheet.cell(row=15, column=excel_column).value)

    notes = (
        "Shares stored as fractions. Historical observation, not forecast. "
        "Production denominator not yet verified; both TWh fields pending."
    )

    if year == 2024:
        notes += (
            " Unresolved source difference: public summary says 98.8%; "
            "workbook gives approximately 98.649%."
        )

    records.append({
        "Year": year,
        "Renewable_share": sheet.cell(10, excel_column).value,
        "Nuclear_share": sheet.cell(20, excel_column).value,
        "Fossil_free_share": sheet.cell(21, excel_column).value,
        "Total_domestic_production_TWh": None,
        "Fossil_production_TWh": None,
        "Data_status": "Historical",
        "Source": (
            "Energimyndigheten, Energiindikatorer i siffror 2026; "
            "local copy: research/2026-10-20/indicators.xlsx"
        ),
        "Source_cells": (
            f"Sheet 6.1: year={sheet.cell(15, excel_column).coordinate}; "
            f"renewable={sheet.cell(10, excel_column).coordinate}; "
            f"nuclear={sheet.cell(20, excel_column).coordinate}; "
            f"fossil_free={sheet.cell(21, excel_column).coordinate}"
        ),
        "Notes": notes,
    })

workbook.close()

historical_data = pd.DataFrame(records).sort_values("Year").reset_index(drop=True)

# Check every historical row.
assert historical_data["Year"].tolist() == list(range(2015, 2025))
assert historical_data["Year"].is_unique

share_columns = [
    "Renewable_share",
    "Nuclear_share",
    "Fossil_free_share",
]

for share_column in share_columns:
    assert historical_data[share_column].notna().all(), f"Missing values in {share_column}"
    assert historical_data[share_column].between(0, 1).all(), f"Invalid fraction in {share_column}"

difference = (
    historical_data["Renewable_share"]
    + historical_data["Nuclear_share"]
    - historical_data["Fossil_free_share"]
)
assert difference.abs().lt(0.000001).all(), "Shares do not reconcile."

# Missing production data must remain missing—not zero.
assert historical_data["Total_domestic_production_TWh"].isna().all()
assert historical_data["Fossil_production_TWh"].isna().all()

output_folder = project_folder / "outputs"
output_folder.mkdir(exist_ok=True)
output_file = output_folder / "electricity_2015_2024.csv"

historical_data.to_csv(output_file, index=False, encoding="utf-8-sig", na_rep="")

# Confirm the exported file still contains ten historical rows.
saved = pd.read_csv(output_file)
assert saved["Year"].tolist() == list(range(2015, 2025))
assert saved["Fossil_production_TWh"].isna().all()

# Display percentages without changing the stored fractions.
preview = historical_data[["Year"] + share_columns].copy()
for share_column in share_columns:
    preview[share_column] = preview[share_column].map(lambda value: f"{value:.4%}")

print(preview.to_string(index=False))
print("\nChecks passed: 10 historical rows; production values remain blank.")
print(f"Saved: {output_file}")
