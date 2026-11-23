"""Check the historical year columns and 2024 electricity shares.

Read the source workbook and print the results without writing any files.
"""

from pathlib import Path

from openpyxl import load_workbook

# Find the workbook relative to this script.
project_folder = Path(__file__).resolve().parent
source_file = (
    project_folder
    / "research"
    / "2026-10-20"
    / "indicators.xlsx"
)

if not source_file.exists():
    raise FileNotFoundError(f"Workbook not found: {source_file}")

# Read saved cell values without changing the workbook.
workbook = load_workbook(
    source_file,
    read_only=True,
    data_only=True,
)
sheet = workbook["6.1"]

# Columns I–R contain 2024 back to 2015.
years = [
    sheet.cell(row=15, column=column).value
    for column in range(9, 19)
]
assert years == list(range(2024, 2014, -1)), (
    f"Unexpected years: {years}"
)

renewable_share = sheet["I10"].value
nuclear_share = sheet["I20"].value
fossil_free_share = sheet["I21"].value

for value in [renewable_share, nuclear_share, fossil_free_share]:
    assert isinstance(value, (int, float)), "Expected a number."
    assert 0 <= value <= 1, "Expected a fraction between 0 and 1."

assert abs(renewable_share + nuclear_share - fossil_free_share) < 0.000001, (
    "Renewable plus nuclear does not match fossil-free."
)

print("Historical years:", years)
print(f"2024 renewable:   {renewable_share:.4%}")
print(f"2024 nuclear:     {nuclear_share:.4%}")
print(f"2024 fossil-free: {fossil_free_share:.4%}")
print("Checks passed.")

workbook.close()
