"""Prepare six annual net-production groups for Power BI page 2 (2015-2024).

Read the SCB source, group production by plant category and export GWh and TWh
with source references and limitations. Preserve the known total differences
and negative pumped-storage values; do not calculate a fossil-production total.
"""

import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "research" / "2026-10-20" / "TAB1010_en.csv"
OUTPUT = ROOT / "outputs" / "dashboard_production.csv"
SOURCE_URL = (
    "https://www.statistikdatabasen.scb.se/pxweb/en/ssd/"
    "START__EN__EN0105__EN0105A/ElProdAr/"
)
YEARS = list(range(2015, 2025))

# Each source production category appears exactly once.
GROUPS = {
    "Hydro": ["hydro"],
    "Wind": ["wind"],
    "Solar": ["solar"],
    "Nuclear": ["nuclear"],
    "Other thermal generation": [
        "main activity producer CHP",
        "autoproducer CHP",
        "condensing turbines",
        "gas-turbines for reserve and others",
    ],
    "Pumped storage": ["pumped storage"],
}
components = [category for members in GROUPS.values() for category in members]
assert len(components) == len(set(components)) == 9
expected_categories = set(components) | {"sum of supply", "import"}

# 1. Read only historical NET observations. Missing markers must raise an error.
with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
    source_rows = list(csv.DictReader(stream))

production_values = {}
for row in source_rows:
    year = int(row["year"])
    if row["observations"] != "Net" or year not in YEARS:
        continue
    key = (year, row["type of power plants"])
    assert key not in production_values, f"Duplicate source key: {key}"
    production_values[key] = int(row["Electricity supply, GWh"])

for year in YEARS:
    actual = {category for y, category in production_values if y == year}
    assert actual == expected_categories, f"Category coverage problem in {year}"
    for category in expected_categories - {"pumped storage"}:
        assert production_values[year, category] >= 0, (year, category)

# 2. Group the nine source categories into six display categories.
dashboard_rows = []
for year in YEARS:
    for label, members in GROUPS.items():
        production_gwh = sum(production_values[year, category] for category in members)
        notes = ["Net production; imports excluded; separate from indicator-workbook shares."]
        if label == "Solar":
            notes.append(
                "2015-2021: estimated from installed capacity and 950 full-load hours."
                if year <= 2021 else
                "2022 onward: source changes to monthly electricity statistics."
            )
        elif label == "Pumped storage":
            notes.append(
                "Own-use reporting changes from modelled to collected values in 2018; "
                "negative net values are retained."
            )
        elif label == "Other thermal generation":
            notes.append("Grouped by plant type; must not be interpreted as entirely fossil.")
        if year in (2015, 2017):
            notes.append(
                "Category sum differs from supply minus imports by "
                f"{1 if year == 2015 else 2} GWh; source values are not adjusted."
            )
        dashboard_rows.append({
            "Year": year,
            "Category": label,
            "Production_GWh": production_gwh,
            # Decimal keeps this conversion from whole GWh to TWh exact.
            "Production_TWh": Decimal(production_gwh) / Decimal(1000),
            "Data_status": "Historical statistics",
            "Source": "SCB, Electricity supply in Sweden by type of power plants, TAB1010",
            "Source_URL": SOURCE_URL,
            "Source_categories": "; ".join(members),
            "Notes": " ".join(notes),
        })

# 3. Check the grouped totals against the independent supply/import control.
assert len(dashboard_rows) == 60
assert len({(r["Year"], r["Category"]) for r in dashboard_rows}) == 60
for year in YEARS:
    grouped_total = sum(r["Production_GWh"] for r in dashboard_rows if r["Year"] == year)
    control = (
        production_values[year, "sum of supply"]
        - production_values[year, "import"]
    )
    # The audit established these differences for this local source version.
    expected_difference = {2015: -1, 2017: -2}.get(year, 0)
    assert control - grouped_total == expected_difference, f"Recheck totals for {year}"

# 4. Export a new table; existing dashboard files stay unchanged.
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(dashboard_rows[0]))
    writer.writeheader()
    writer.writerows(dashboard_rows)

# Reopen to verify that CSV serialization preserved every value and note.
with OUTPUT.open(encoding="utf-8-sig", newline="") as stream:
    saved = list(csv.DictReader(stream))
assert saved == [{key: str(value) for key, value in row.items()} for row in dashboard_rows]
assert sum(Decimal(r["Production_TWh"]) < 0 for r in saved) == 3

print("2024 net production (TWh)")
for row in dashboard_rows:
    if row["Year"] == 2024:
        print(f"{row['Category']:<26} {row['Production_TWh']:>8.3f}")
print("\nChecks passed: 60 rows; 10 years; 6 categories; source totals reconciled.")
print("Negative pumped-storage values retained: 3.")
print("No fossil-TWh estimate was calculated.")
print(f"Saved: {OUTPUT}")
