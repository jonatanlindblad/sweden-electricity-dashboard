# Sweden electricity dashboard

A Python and Power BI project about Sweden's domestic electricity production in 2015–2024. It also explores what continuing historical changes in the fossil-free share would imply for 2040.

The dashboard has four pages:

1. Historical renewable, nuclear and fossil shares, with two conditional fossil-free scenarios.
2. Net production by generation category and the change from 2015 to 2024.
3. Sensitivity of the scenarios to the historical period used to fit the trend.
4. Published direct CO₂ intensity of electricity production.

View the [four-page dashboard PDF](outputs/sweden_electricity_dashboard_v5.pdf). The seven CSV files in `outputs/` contain the analysis results and Power BI inputs. The editable Power BI report and data model are not included.

## Project structure

- Root Python files: data checks, calculations and dashboard exports.
- `research/`: source notes, manifests (records of source files and URLs), and two AIB download/extraction scripts. Full downloaded documents stay local.
- `outputs/`: the products of the analysis, including CSV tables and the latest dashboard PDF.
- [methods_note.md](methods_note.md): calculations, assumptions and limitations.
- [SOURCES.md](SOURCES.md): attribution, sharing terms and how to restore required source files.
- [repository_review.md](repository_review.md): repository contents and checks before sharing updates.

## Set up Python

Use Python 3.12 and the package versions in [requirements.txt](requirements.txt). The full analysis sequence passed with this setup. The file fixes the versions of the three packages used directly by the scripts; it does not fix every package they depend on.

From the project folder, create a virtual environment: a folder containing this project's Python packages. If `.venv` already exists, use a different folder name in both commands below to preserve it.

macOS/Linux:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`pandas` handles tables, `openpyxl` reads Excel files, and `pypdf` extracts PDF text. Python supplies the other imported modules. Do not use `python -O`: the scripts use `assert` checks, which that option disables.

A fresh package installation has not been tested. Results were compared with the existing Python 3.14 setup; small differences in the final decimal places did not change displayed values. See [validation details](methods_note.md#validation).

## Restore the inputs

The saved CSVs and PDF can be viewed without running Python. A new checkout needs local source files before regenerating the complete analysis. Follow [SOURCES.md](SOURCES.md) to restore:

- `research/2026-10-20/indicators.xlsx`
- `research/2026-10-20/TAB1010_en.csv`
- The ten selected AIB PDFs and three Excel workbooks in `research/2026-11-19/aib/`.

The manifests record source URLs, filenames and file fingerprints. A fingerprint identifies a file's exact contents. The scripts check AIB fingerprints, so review a changed source file before updating its recorded fingerprint.

## Run the analysis

Run the following commands from the project folder, in order, after activating the environment and restoring the inputs. Stop and investigate if any command fails. Export scripts overwrite their named generated files in `outputs/`.

```sh
python check_electricity_data.py
python prepare_electricity_data.py
python check_domestic_production.py
python calculate_scenarios.py
python prepare_dashboard_mix.py
python prepare_dashboard_trends.py
python check_production_categories.py
python prepare_dashboard_production.py
python check_scenario_sensitivity.py
python prepare_dashboard_sensitivity.py
python research/2026-11-19/extract_aib_intensity.py
python prepare_dashboard_co2_intensity.py
```

| Script | What it does / writes |
|---|---|
| `check_electricity_data.py` | Checks workbook years and selected 2024 shares; prints results. |
| `prepare_electricity_data.py` | Writes `electricity_2015_2024.csv`, 10 historical rows; production fields initially blank. |
| `check_domestic_production.py` | Checks SCB supply minus imports and writes `electricity_analysis_2015_2024.csv`, 10 rows. |
| `calculate_scenarios.py` | Prints two conditional scenarios; writes no CSV. |
| `prepare_dashboard_mix.py` | Writes `dashboard_historical_mix.csv`, 30 rows: 10 years × 3 categories. |
| `prepare_dashboard_trends.py` | Writes `dashboard_fossil_free_trends.csv`, 38 historical/scenario points. |
| `check_production_categories.py` | Checks SCB categories, totals and source exceptions; writes no CSV. |
| `prepare_dashboard_production.py` | Writes `dashboard_production.csv`, 60 rows: 10 years × 6 categories. |
| `check_scenario_sensitivity.py` | Prints results for six overlapping historical periods; writes no CSV. |
| `prepare_dashboard_sensitivity.py` | Writes `dashboard_sensitivity.csv`, six rows; checks agreement with scenario endpoints. |
| `research/2026-11-19/extract_aib_intensity.py` | Reads selected archived reports and writes `aib/sweden_production_co2_verified.json`, 10 records with references and checks. |
| `prepare_dashboard_co2_intensity.py` | Writes `dashboard_co2_intensity.csv`, 10 annual published estimates. |

The remaining script, `research/2026-11-19/download_aib_sources.py`, downloads a new AIB archive and refuses to overwrite an existing folder. To investigate new sources, set a new destination in that script and review the documents before changing the extraction settings. To restore the existing inputs, follow SOURCES instead: numbered filenames from a new download may differ if the website's links change.

## Connect the outputs to Power BI

Import the five `dashboard_*.csv` files as separate tables. The two `electricity_*.csv` files are intermediate analysis tables. After running Python, refresh the CSV data in Power BI separately. Python does not update the online report or its layout.

| CSV / table | Main fields and use |
|---|---|
| `dashboard_historical_mix.csv` / HistoricalMix | `Year`, `Category`, `Share`: stacked historical mix. Store Share as a decimal fraction and format as percentage. |
| `dashboard_fossil_free_trends.csv` / FossilFreeTrends | `Year`, `Series`, `Share`: line chart. Keep Year decimal and use a continuous axis to preserve the fractional 100% crossing. Format Share as percentage. |
| `dashboard_production.csv` / Production | `Year`, `Category`, `Production_TWh`: annual production. Endpoint change is 2024 minus 2015 for each category. |
| `dashboard_sensitivity.csv` / Sensitivity | `Trend_period`, `Slope_pp_per_year`, `Outcome_by_2040`: comparison of historical windows. Slope is a decimal number in percentage points/year, not percentage formatting. Anchor_share and Share_2040 are fractions suitable for percentage formatting. |
| `dashboard_co2_intensity.csv` / CO2Intensity | `Year`, `CO2_g_per_kWh`, `Factor_period`: annual columns, decimal intensity in g CO₂/kWh. Use Factor_period to mark the 2022 method boundary. |

Sort years ascending. Keep blank 2040 sensitivity shares blank: those scenarios ended at the 100% boundary earlier. Use one annual intensity value per year (for example Average when there is exactly one row); do not sum intensities across years. Do not add together all three historical share categories across multiple years.

Each page can use its own table. Remove unnecessary automatically created relationships; CO2Intensity should not serve as the shared list of years for other tables. These are setup instructions; the current online data model has not been checked against them.

## Interpretation and limitations

Fossil-free share = renewable share + nuclear share. Shares concern domestic production, not imports or consumption. The scenarios assume that a fitted annual change continues from the observed 2024 share. Chart lines end at 2040 or 100%, whichever comes first. These are conditional examples, not forecasts or probabilities of reaching the goal.

The workbook gives a 2024 fossil-free share of about 98.65%, compared with 98.8% in a published summary; the difference remains unresolved. SCB production volumes are kept separate from the workbook's shares because their compatibility has not been established. The project therefore does not estimate fossil electricity production in TWh.

AIB's CO₂ intensity measures emissions per unit of electricity, excluding biogenic CO₂ and lifecycle emissions. Its emission-factor source changed in 2022, so year-to-year differences can reflect both production and method changes. Lower intensity alone does not establish lower annual emissions. The [methods note](methods_note.md) explains the calculations, source differences and other limitations.

The analysis and charts use statistics from Energimyndigheten, Statistics Sweden and AIB. They are the project's calculations and presentation, not official agency results. Source references are retained in the data files.

## Coding style

Use descriptive `snake_case` names (words separated by underscores), four-space indentation and paths relative to the script. Comments should explain units, decisions and source exceptions. Keep missing values distinct from zero and preserve data checks when simplifying code. Before changing a calculation, save its output; afterward, compare values, row counts, units, references and known exceptions.

AI tools supported code development, source research, validation and documentation.

Source data retain their own [sharing terms](SOURCES.md). The project's code has no licence assigned.
