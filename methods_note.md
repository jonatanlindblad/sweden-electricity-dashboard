# Methods note

## Question and scope

How far is Sweden from 100% fossil-free electricity production, and what would continuing historical trends imply for 2040?

The dashboard covers domestic electricity production in 2015–2024. It does not assess imported-electricity emissions, lifecycle emissions or grid reliability. Sources and sharing terms are listed in [SOURCES.md](SOURCES.md).

## Historical shares

Annual shares come from Energimyndigheten's *Energiindikatorer i siffror 2026*, sheet 6.1. Forecast columns are excluded. Shares are stored as fractions and displayed as percentages:

- Fossil-free share = renewable share + nuclear share.
- Fossil share = 1 − fossil-free share.

The workbook gives about 98.65% fossil-free production for 2024. The published summary gives 98.8%; this difference remains unresolved.

## Production volumes and categories

SCB table TAB1010 provides net production data for 2015–2024. Net production accounts for electricity used by the plants themselves. Domestic production is calculated as supply minus imports. Dividing GWh by 1,000 converts it to TWh. Production is grouped into hydro, wind, solar, nuclear, other thermal generation and pumped storage. Other thermal generation can include fossil-free fuels, so it is not treated as fossil generation.

SCB volumes and the indicator workbook's shares are kept separate because their compatibility has not been established. They are not combined to estimate fossil electricity production in TWh.

The source's production categories add up to 1 GWh more than supply minus imports in 2015 and 2 GWh more in 2017. These differences are reported without adjusting the source values. Negative net pumped-storage values in 2015–2017 are also retained. The method for reporting pumped storage's own electricity use changed in 2018. Solar production was estimated from installed capacity through 2021; its source changed in 2022.

The production-change chart subtracts 2015 values from 2024 values. It shows the size of the changes, not their causes.

## Conditional scenarios

A straight line is fitted to all annual observations in each of two periods: 2020–2024 (five observations) and 2015–2024 (ten observations). Its slope is the fitted annual change in fossil-free share.

Each scenario uses that slope but starts from the observed 2024 share, rather than the fitted line's value:

**Scenario share = 2024 share + fitted annual slope × (year − 2024)**

The assumption is that the fitted annual change continues unchanged. Chart lines end at 2040 or the exact 100% crossing, whichever comes first. They neither exceed 100% nor continue along a flat line at 100%.

These scenarios do not model future policy, investment, demand or changes in individual generation technologies. They describe the result of the stated assumption, not a forecast of what will happen.

## Sensitivity to the historical period

Six periods start in 2015 through 2020 and all end in 2024. The shortest period, 2020–2024, contains five annual observations; starting later would use fewer observations. The same fitting method is used for each period, and every scenario starts from the observed 2024 share. Slopes are stored as changes in a decimal fraction and multiplied by 100 to report percentage points per year.

| Historical period | Slope (percentage points/year) | Conditional result |
|---|---:|---|
| 2015–2024 | 0.1353 | Reaches 100% at mathematical year 2033.99. |
| 2020–2024 | 0.0717 | Reaches 99.7956% in 2040. |

Five of the six scenarios reach 100% before 2040. Their 2040 shares are left blank because the lines have already ended. A blank is not zero.

The periods overlap and contain different numbers of observations. The comparison shows sensitivity to the period chosen; it does not give independent forecasts or a probability of reaching 100%. It also does not establish the causes of change or prove sustained slowing.

## Direct CO₂ intensity

AIB's published Swedish production-mix estimates provide one value per year for 2015–2024, measured in grams of CO₂ per kilowatt-hour (g CO₂/kWh). The values describe the whole production mix, without separating fossil and fossil-free generation emissions. They are not residual-mix or consumption values.

AIB's measure excludes biogenic CO₂ (CO₂ from biological material such as biomass) and lifecycle emissions. It does not represent all greenhouse gases, total annual emissions or avoided emissions. Fossil-free generation can still release physical biogenic CO₂. These values are published estimates, not measurements of all national stack emissions.

Emission factors are values used to estimate emissions from electricity generation. The series uses each year's published results rather than recalculating every year with the same factors. AIB changed its input emission-factor source in 2022, and generation inputs also vary across reports. Year-to-year differences can therefore reflect both production and data or method changes. Lower intensity alone does not establish lower annual emissions. The project does not convert this series to annual tonnes using the separate SCB net-production totals.

PDF values have whole-number precision for 2015–2018 and two decimal places for 2019–2024. Comparisons with the 2022–2024 workbooks allow a rounding difference of 0.005 g CO₂/kWh. The 2024 PDF value is 5.05 g CO₂/kWh, displayed as 5.1 in the chart.

The [emissions source review](research/2026-11-19/emissions_source_review.md) records the selected values, report locations and reasons for choosing this measure. File fingerprints identify source versions; they do not establish the accuracy of the source estimates.

## Validation

On 23 November 2026, the 12-command sequence in the [README](README.md#run-the-analysis) passed in a separate project copy with the archived inputs. The environment used Python 3.12.14, pandas 2.2.3, openpyxl 3.1.5 and pypdf 6.21.4, matching [requirements.txt](requirements.txt).

`electricity_2015_2024.csv`, `dashboard_production.csv`, `dashboard_co2_intensity.csv` and the verified AIB JSON matched the saved files exactly. The other four CSVs differed only in final decimal places compared with the Python 3.14 development setup (pandas 3.1.1 and openpyxl 3.1.5). Column names, row counts, text, references, notes and blank cells matched exactly; displayed values agreed.

Numeric comparisons allowed absolute differences of `1e-14` for shares and slopes and `1e-12` for fractional crossing years. These small allowances account for calculation differences between environments; they do not estimate uncertainty in the source data. The saved outputs were not replaced by the comparison files.

The AIB downloader was tested separately without live downloads. A fresh package installation and downloading all original inputs again from live URLs have not been tested. The checks cover extraction, calculations and agreement between files, not the scientific accuracy of every published estimate.

## Reproduction and attribution

See [SOURCES.md](SOURCES.md) for source credits, sharing terms and input files, and [README.md](README.md) for the script sequence and Power BI setup. Calculations and charts are this project's work based on those sources, not official agency results.
