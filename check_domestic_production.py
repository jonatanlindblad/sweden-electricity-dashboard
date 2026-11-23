"""Check SCB domestic production and add it to the historical shares table.

Save a separate analysis CSV with production totals, source references and
limitations. Keep fossil production blank because compatibility between the
SCB totals and the indicator-workbook shares has not been established.
"""

from pathlib import Path

import pandas as pd

project_folder = Path(__file__).resolve().parent

source_file = (
    project_folder
    / "research"
    / "2026-10-20"
    / "TAB1010_en.csv"
)

source_data = pd.read_csv(source_file)

# Keep net observations for the ten historical years.
net_data = source_data.loc[
    source_data["observations"].eq("Net")
    & source_data["year"].between(2015, 2024)
].copy()

net_data["Electricity supply, GWh"] = pd.to_numeric(
    net_data["Electricity supply, GWh"],
    errors="raise",
)

assert not net_data.duplicated(["year", "type of power plants"]).any()

# One row per year, one column per production/supply category.
production_by_year = net_data.pivot(
    index="year",
    columns="type of power plants",
    values="Electricity supply, GWh",
).sort_index()

assert production_by_year.index.tolist() == list(range(2015, 2025))
assert production_by_year.notna().all().all(), "Missing source values."

# Supply includes imports.
domestic_gwh = production_by_year["sum of supply"] - production_by_year["import"]

# Cross-check against the sum of domestic generation categories.
generation_columns = production_by_year.columns.difference(
    ["sum of supply", "import"]
)
component_sum_gwh = production_by_year[generation_columns].sum(axis=1)

audit = pd.DataFrame({
    "Supply_GWh": production_by_year["sum of supply"],
    "Imports_GWh": production_by_year["import"],
    "Domestic_GWh": domestic_gwh,
    "Components_GWh": component_sum_gwh,
})

audit["Difference_GWh"] = (
    audit["Domestic_GWh"] - audit["Components_GWh"]
)
audit["Domestic_TWh"] = audit["Domestic_GWh"] / 1000

print(audit.to_string())

assert domestic_gwh.gt(0).all()
assert audit["Difference_GWh"].abs().le(2).all(), (
    "Difference exceeds 2 GWh; investigate before proceeding."
)

# Compare a known component's share across the two sources.
analysis_data = pd.read_csv(
    project_folder / "outputs" / "electricity_2015_2024.csv"
)

workbook_nuclear_share = analysis_data.loc[
    analysis_data["Year"].eq(2024), "Nuclear_share"
].item()

scb_nuclear_share = (
    production_by_year.loc[2024, "nuclear"] / domestic_gwh.loc[2024]
)

print("\n2024 source comparison")
print(f"SCB domestic production: {domestic_gwh.loc[2024] / 1000:.3f} TWh")
print(f"SCB nuclear share:      {scb_nuclear_share:.4%}")
print(f"Workbook nuclear share: {workbook_nuclear_share:.4%}")

# Add SCB domestic production by matching each row's year.
analysis_data["Total_domestic_production_TWh"] = (
    analysis_data["Year"].map(domestic_gwh / 1000)
)

# Keep unsupported fossil-production values missing.
assert analysis_data["Fossil_production_TWh"].isna().all()

# Record separate provenance for the production measure.
analysis_data["Production_source"] = (
    "SCB, Electricity supply by type of power plants; "
    "local copy: research/2026-10-20/TAB1010_en.csv"
)

analysis_data["Production_method"] = (
    "Net sum of supply minus imports, divided by 1000: GWh to TWh. "
    "Separate context; not verified as the denominator for workbook shares."
)

# Preserve the differences found in our component check.
analysis_data["Production_check_difference_GWh"] = analysis_data["Year"].map(
    audit["Difference_GWh"]
)

# Update the old note now that domestic production has been added.
analysis_data["Notes"] = analysis_data["Notes"].str.replace(
    "Production denominator not yet verified; both TWh fields pending.",
    (
        "SCB domestic production added as separate context. "
        "Compatibility with indicator shares unresolved; fossil TWh blank."
    ),
    regex=False,
)

analysis_data = analysis_data.sort_values("Year").reset_index(drop=True)

# Final checks before saving.
assert analysis_data["Year"].tolist() == list(range(2015, 2025))
assert analysis_data["Total_domestic_production_TWh"].notna().all()
assert analysis_data["Total_domestic_production_TWh"].gt(0).all()
assert analysis_data["Production_check_difference_GWh"].notna().all()
assert analysis_data["Fossil_production_TWh"].isna().all()

value_2024 = analysis_data.loc[
    analysis_data["Year"].eq(2024), "Total_domestic_production_TWh"
].item()
assert abs(value_2024 - 169.265) < 0.000001

# Save a new file, preserving the earlier shares-only table.
output_file = (
    project_folder / "outputs" / "electricity_analysis_2015_2024.csv"
)
analysis_data.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig",
    na_rep="",
)

# Check that missing values remain missing after export.
saved = pd.read_csv(output_file)
assert len(saved) == 10
assert saved["Total_domestic_production_TWh"].notna().all()
assert saved["Fossil_production_TWh"].isna().all()
assert "98.8%" in saved.loc[saved["Year"].eq(2024), "Notes"].item()

print("\nUpdated analysis table:")
print(
    saved[
        ["Year", "Total_domestic_production_TWh", "Fossil_production_TWh"]
    ].to_string(index=False)
)
print("\nChecks passed: domestic production added; fossil TWh remains blank.")
print(f"Saved: {output_file}")