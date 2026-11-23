# Sources, local inputs and sharing

Source terms reviewed 23 November 2026. The repository includes selected statistical extracts and the dashboard PDF. Full source reports, workbooks and other research downloads stay local. The terms below apply to the data even when they are shared separately from the code.

## Attribution and terms

- **Energimyndigheten:** historical shares from *Energiindikatorer i siffror 2026*, sheet 6.1. Its [statistics terms](https://www.energimyndigheten.se/statistik/statistik/anvandarvillkor/) permit copying and sharing published statistics with attribution. Label processed statistics as the project's calculations based on agency data. The broader [website copyright terms](https://www.energimyndigheten.se/om-oss/om-webbplatsen/) distinguish freely reusable and protected material. This repository includes selected values and source records, not the complete workbook.
- **Statistics Sweden (SCB):** [TAB1010 electricity supply by type of power plant](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__EN__EN0105__EN0105A/ElProdAr/). SCB's [terms](https://www.scb.se/om-scb/om-scb.se-och-anvandningsvillkor/) identify statistical-database open data as CC0 and distinguish other website material. The source fields credit SCB; regrouping categories and calculating changes are this project's work, not official SCB results.
- **Association of Issuing Bodies (AIB):** Swedish production-mix results in the [European Residual Mix reports](https://www.aib-net.org/facts/european-residual-mix), 2015–2024. AIB's [FAQ](https://www.aib-net.org/faq/residual-mix) permits use of report data with attribution. The selected 2022, 2023 and 2024 PDFs restrict selling or distributing the underlying country/technology emission factors, or processing them as part of a derivative tool. This project uses published aggregate Swedish production-mix results. Full reports and workbooks, including the restricted annex material, are excluded from Git.

Any future code licence must remain separate from these data terms. Keep source credits and limitations with shared CSVs and dashboard exports.

## Restore the original non-AIB inputs

Create `research/2026-10-20/` if necessary. [source_manifest.json](research/2026-10-20/source_manifest.json) records the original URLs and local filenames. Use the full `url`, including query parameters, rather than a shortened `resolved_url`.

1. Download the `indicators.xlsx` entry and save it under that exact name.
2. Download the production ZIP linked in the `production.html` entry and extract `TAB1010_en.csv` into the same folder.
3. Compare their SHA-256 fingerprints with [source_checksums.json](research/2026-10-20/source_checksums.json). A fingerprint identifies a file's exact contents. These were recorded from the local copies on 23 November 2026.

On macOS, from the project folder:

```sh
shasum -a 256 research/2026-10-20/indicators.xlsx
shasum -a 256 research/2026-10-20/TAB1010_en.csv
```

A source file may have been revised since it was downloaded. Exact reproduction requires the original contents; review revisions and rerun the checks before adopting a new version. Downloading all originals again from the live websites has not been tested. Other manifest entries record background research; the lifecycle and fuel workbooks are not required to run the dashboard scripts.

## Restore the selected AIB files

Create or use `research/2026-11-19/aib/`. Its [manifest.json](research/2026-11-19/aib/manifest.json) maps each filename below to the exact original URL and SHA-256 fingerprint. Download from those URLs and save with the listed local names; do not infer names from the current order of website links.

| Year | Required PDF | Required cross-check workbook |
|---|---|---|
| 2015 | `2015_1.pdf` | — |
| 2016 | `2016_0.pdf` | — |
| 2017 | `2017_0.pdf` | — |
| 2018 | `2018_0.pdf` | — |
| 2019 | `2019_0.pdf` | — |
| 2020 | `2020_0.pdf` | — |
| 2021 | `2021_0.pdf` | — |
| 2022 | `2022_1.pdf` | `2022_0.xlsx` |
| 2023 | `2023_1.pdf` | `2023_2.xlsx` |
| 2024 | `2024_0.pdf` | `2024_1.xlsx` |

The extraction script checks file fingerprints, report years, production-mix headings and Swedish values. It compares the three workbooks with the PDF values, allowing for rounding, then writes the [verified JSON extract](research/2026-11-19/aib/sweden_production_co2_verified.json). The dashboard export script also needs the ten PDFs for fingerprint checks, even when that JSON file already exists.

Keep the manifest's original retrieval dates when restoring identical files. For a new source version, record its download date, URL and fingerprint, then review the page locations and methodology before using it.

The general AIB downloader creates a fresh archive and stops if its chosen folder already exists. It is not a restoration tool for a checkout that already contains the manifest and verified JSON.

## Source records and interpretation

The JSON extract records PDF filenames, URLs, page references, extracted rows, fingerprints, published precision and workbook comparisons. Source and method fields in the dashboard CSVs connect the results to these records.

The [methods note](methods_note.md) describes unresolved discrepancies, source boundaries and method changes. The [research review](research/2026-11-19/emissions_source_review.md) preserves why annual emissions in tonnes were not selected and why direct intensity was selected instead.
