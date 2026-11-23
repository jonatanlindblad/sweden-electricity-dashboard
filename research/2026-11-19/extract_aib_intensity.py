"""Extract Sweden's published production-mix CO2 values, not residual mixes.

Run with the bundled Python (pypdf and pandas). The dashboard preparation
script needs only the Python standard library and this verified JSON snapshot.
"""
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re

import pandas as pd
from pypdf import PdfReader

archive_folder = Path(__file__).resolve().parent / "aib"
manifest_records = json.loads((archive_folder / "manifest.json").read_text())
manifest_by_filename = {}
for record in manifest_records:
    # Failed downloads have no local file, so exclude them from this lookup.
    if "file" in record:
        manifest_by_filename[record["file"]] = record

# Each entry identifies the filename, heading page, and value page.
# Page numbers start at 1 and were checked against the printed page labels.
SOURCES = {
    2015: ("2015_1.pdf", 14, 14),
    2016: ("2016_0.pdf", 18, 18),
    2017: ("2017_0.pdf", 18, 18),
    2018: ("2018_0.pdf", 19, 20),
    2019: ("2019_0.pdf", 17, 18),
    2020: ("2020_0.pdf", 17, 18),
    2021: ("2021_0.pdf", 17, 18),
    2022: ("2022_1.pdf", 22, 24),
    2023: ("2023_1.pdf", 22, 23),
    2024: ("2024_0.pdf", 22, 23),
}
WORKBOOKS = {2022: ("2022_0.xlsx", "Production Mix 2022"),
             2023: ("2023_2.xlsx", "Production Mix"),
             2024: ("2024_1.xlsx", "Production Mix")}

intensity_records = []
for year, (filename, heading_page, value_page) in SOURCES.items():
    source_file = archive_folder / filename
    assert sha256(source_file.read_bytes()).hexdigest() == manifest_by_filename[filename]["sha256"]
    pdf = PdfReader(source_file)
    # Python counts pages from zero: PDF page 14 is pdf.pages[13].
    page_text = pdf.pages[value_page - 1].extract_text()
    heading_text = pdf.pages[heading_page - 1].extract_text()
    assert f"{year}" in pdf.pages[0].extract_text()
    assert "gCO2" in page_text
    if year == 2015:
        assert "Figure 5: Direct CO2 emissions for Production Mix" in heading_text
        country_line = next(line for line in page_text.splitlines() if line.startswith("AT BE BG"))
        countries = country_line.split()
        production_line = next(line for line in page_text.splitlines() if line.startswith("Production Mix "))
        values = production_line.removeprefix("Production Mix ").split()
        assert len(countries) == len(values) and countries.count("SE") == 1
        published_value = values[countries.index("SE")]
        source_row = production_line
        source_reference = "Figure 5, Production Mix row, SE column, p. 14"
    else:
        assert re.search(r"Table\s+5:\s+Production Mix", heading_text)
        sweden_rows = [line.strip() for line in page_text.splitlines() if line.strip().startswith("SE ")]
        assert len(sweden_rows) == 1
        source_row = sweden_rows[0]
        # Last two columns are CO2 intensity and radioactive waste respectively.
        published_value = source_row.split()[-2].replace(",", ".")
        source_reference = f"Table 5, Production Mix, SE row, p. {value_page}"
    # Preserve the decimal places shown in the PDF, including trailing zeros.
    intensity_value = Decimal(published_value)
    assert intensity_value.is_finite() and intensity_value >= 0
    workbook_crosscheck = None
    if year in WORKBOOKS:
        workbook_filename, sheet_name = WORKBOOKS[year]
        assert sha256((archive_folder / workbook_filename).read_bytes()).hexdigest() == manifest_by_filename[workbook_filename]["sha256"]
        workbook_data = pd.read_excel(archive_folder / workbook_filename, sheet_name=sheet_name)
        workbook_data.columns = [str(column_name).strip() for column_name in workbook_data.columns]
        sweden_values = workbook_data.loc[workbook_data.iloc[:, 0].eq("SE"), "CO2 (gCO2/kWh)"]
        assert len(sweden_values) == 1
        workbook_value = float(sweden_values.iloc[0])
        # The PDF rounds these years to two decimal places (half a step is 0.005).
        assert abs(workbook_value - float(intensity_value)) <= 0.005
        workbook_crosscheck = {"file": workbook_filename, "sheet": sheet_name, "value": workbook_value,
                         "column": "CO2 (gCO2/kWh)", "country_code": "SE"}
    intensity_records.append({
        "Year": year, "Country": "Sweden", "Country_code": "SE",
        "Mix": "Production mix", "CO2_g_per_kWh": float(intensity_value),
        "Published_value": published_value,
        "Source_precision_decimals": max(0, -intensity_value.as_tuple().exponent),
        "Source_file": filename, "Source_URL": manifest_by_filename[filename]["url"],
        "Source_reference": source_reference, "Source_row": source_row,
        "Source_sha256": manifest_by_filename[filename]["sha256"],
        "Workbook_crosscheck": workbook_crosscheck,
    })

assert [record["Year"] for record in intensity_records] == list(range(2015, 2025))
output_file = archive_folder / "sweden_production_co2_verified.json"
output_file.write_text(json.dumps(intensity_records, indent=2, ensure_ascii=False) + "\n")
for record in intensity_records:
    print(record["Year"], record["Published_value"], record["Source_reference"])
print("Checked: 10 annual production-mix values; 2022–2024 match source workbooks at PDF precision.")
