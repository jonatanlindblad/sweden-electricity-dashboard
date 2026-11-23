"Audit the existing SCB production file without changing any data files."

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "research" / "2026-10-20" / "TAB1010_en.csv"
YEARS = list(range(2015, 2025))

# These categories are mutually exclusive in the selected SCB table.
# Thermal is a plant grouping, not a fossil-fuel classification.
GROUPS = {
    "Hydro": ["hydro"],
    "Wind": ["wind"],
    "Solar": ["solar"],
    "Nuclear": ["nuclear"],
    "Other thermal": [
        "main activity producer CHP",
        "autoproducer CHP",
        "condensing turbines",
        "gas-turbines for reserve and others",
    ],
    "Pumped storage": ["pumped storage"],
}
COMPONENTS = [name for members in GROUPS.values() for name in members]
EXPECTED = set(COMPONENTS) | {"sum of supply", "import"}

with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
    source_rows = list(csv.DictReader(stream))

selected_rows = [
    row for row in source_rows
    if row["observations"] == "Net" and int(row["year"]) in YEARS
]
# Store each GWh value under a (year, source category) pair.
# This pair is a dictionary key: it identifies one observation for lookup.
production_values = {}
for row in selected_rows:
    key = (int(row["year"]), row["type of power plants"])
    assert key not in production_values, f"Duplicate year/category: {key}"
    # int deliberately rejects blanks and SCB missing-value markers such as '..'.
    production_values[key] = int(row["Electricity supply, GWh"])

for year in YEARS:
    actual = {category for y, category in production_values if y == year}
    assert actual == EXPECTED, f"Unexpected/missing categories in {year}: {actual ^ EXPECTED}"
    for category in EXPECTED - {"pumped storage"}:
        assert production_values[year, category] >= 0, (year, category)

print("Coverage: 2015-2024, Net, GWh")
print(f"Records: {len(production_values)} (90 production records + 20 supply/import records)")
print("Duplicate keys: 0; missing or non-integer values: 0")
print("\nAnnual reconciliation (GWh)")
print(f"{'Year':<6}{'Supply-import':>16}{'Components':>14}{'Difference':>14}")
differences = []
for year in YEARS:
    domestic = (
        production_values[year, "sum of supply"]
        - production_values[year, "import"]
    )
    components = sum(production_values[year, category] for category in COMPONENTS)
    difference = domestic - components
    differences.append(difference)
    print(f"{year:<6}{domestic:>16,}{components:>14,}{difference:>14,}")

# Retain the 2 GWh investigation threshold used in the earlier project audit.
# Do not silently adjust individual categories to force an exact match.
assert max(abs(d) for d in differences) <= 2, "Difference exceeds 2 GWh; investigate."

print("\nProposed display groups (TWh = GWh / 1000)")
print(f"{'Category':<20}{'2015':>12}{'2024':>12}{'Change':>12}")
for label, members in GROUPS.items():
    start = sum(production_values[2015, c] for c in members) / 1000
    end = sum(production_values[2024, c] for c in members) / 1000
    print(f"{label:<20}{start:>12.3f}{end:>12.3f}{end-start:>12.3f}")

print("\nNegative net pumped-storage observations (GWh):")
for year in YEARS:
    value = production_values[year, "pumped storage"]
    if value < 0:
        print(f"  {year}: {value}")

print("\nSource notes to retain:")
print("- Solar: estimated from installed capacity through 2021; source changes from 2022.")
print("- Pumped storage: own-use method changes from 2018; preserve negative net values.")
print("- Thermal generation is not equivalent to fossil generation.")
print("- Small rounding differences remain visible; no source values are adjusted.")
print("- This file contains 2025 too, but this project deliberately uses 2015-2024.")
print("- SCB volumes are separate from the indicator workbook's shares.")
print("\nAudit complete. No CSV files were created or changed.")
