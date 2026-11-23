"""Prepare annual direct CO2 intensity for Power BI from verified AIB extracts.

Values retain the precision of AIB's annual PDF reports. This script does not
calculate emission factors, annual tonnes, lifecycle emissions or avoided CO2.
Uses Python's standard library, so no extra package installation is needed.
"""
import csv
from hashlib import sha256
import json
import math
from pathlib import Path

project_folder = Path(__file__).resolve().parent
archive_folder = project_folder / "research" / "2026-11-19" / "aib"
source_records = json.loads((archive_folder / "sweden_production_co2_verified.json").read_text())
assert [record["Year"] for record in source_records] == list(range(2015, 2025))

dashboard_rows = []
for source_record in source_records:
    assert source_record["Country_code"] == "SE" and source_record["Mix"] == "Production mix"
    assert sha256((archive_folder / source_record["Source_file"]).read_bytes()).hexdigest() == source_record["Source_sha256"]
    intensity_value = source_record["CO2_g_per_kWh"]
    assert math.isfinite(intensity_value) and intensity_value >= 0
    assert intensity_value == float(source_record["Published_value"])
    year = source_record["Year"]
    dashboard_rows.append({
        "Year": year,
        "Country": "Sweden",
        "CO2_g_per_kWh": intensity_value,
        "Unit": "g CO2/kWh",
        "Mix": "Production mix",
        "Data_status": "Historical published estimate",
        "Factor_period": "2015-2021" if year < 2022 else "2022-2024",
        "Method_change": "AIB changed input emission-factor source in 2022" if year == 2022 else "",
        "Source_precision_decimals": source_record["Source_precision_decimals"],
        "Source": f"AIB, European Residual Mixes {year}, production mix",
        "Source_URL": source_record["Source_URL"],
        "Source_reference": source_record["Source_reference"],
        "Notes": (
            "Direct CO2 intensity of domestic electricity production under AIB's methodology. "
            "Excludes biogenic CO2 and lifecycle emissions; not all greenhouse gases. "
            "Not residual mix, electricity consumption or annual tonnes. "
            "As-published annual series, not recalculated with a common factor set. "
            "Input emission-factor source changed in 2022; generation inputs also vary by report. "
            "Changes cannot be attributed solely to changes in generation. "
            "2015-2018 values are published as whole g CO2/kWh; 2019-2024 to two decimals."
        ),
    })

output_file = project_folder / "outputs" / "dashboard_co2_intensity.csv"
output_file.parent.mkdir(exist_ok=True)
with output_file.open("w", newline="", encoding="utf-8-sig") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(dashboard_rows[0]))
    writer.writeheader()
    writer.writerows(dashboard_rows)

# Read the CSV back to check that saving preserved the years and numeric values.
with output_file.open(newline="", encoding="utf-8-sig") as stream:
    saved_rows = list(csv.DictReader(stream))
assert len(saved_rows) == 10
assert [int(record["Year"]) for record in saved_rows] == list(range(2015, 2025))
assert [float(record["CO2_g_per_kWh"]) for record in saved_rows] == [record["CO2_g_per_kWh"] for record in dashboard_rows]
assert sum(bool(record["Method_change"]) for record in saved_rows) == 1

print("Year   Direct CO2 (g/kWh)")
for record in source_records:
    print(f"{record['Year']}   {record['Published_value']:>8}")
print("\nChecks passed: 10 years; Sweden; production mix; source hashes; CSV round-trip.")
print("Numeric decimal, not percentage. Do not sum intensities across years.")
print("Method change in 2022. Biogenic CO2 and lifecycle emissions excluded.")
print(f"Saved: {output_file}")
