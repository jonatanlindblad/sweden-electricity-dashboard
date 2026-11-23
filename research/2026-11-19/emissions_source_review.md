# CO₂ intensity: source selection

Sources reviewed 19 November 2026; extraction completed and documentation updated by 23 November 2026.

The dashboard uses **AIB's direct CO₂ intensity of Swedish electricity production**, measured in g CO₂/kWh. The series covers 2015–2024 and appears in the [four-page dashboard PDF](../../outputs/sweden_electricity_dashboard_v5.pdf).

The source search also considered annual emissions in tonnes, with fossil and biogenic CO₂ reported separately. The reviewed sources did not provide a verified electricity-only series matching that scope. Intensity was selected instead; it answers a different question: how much CO₂ is reported per unit of electricity produced.

## Selected values and checks

AIB's production mix covers electricity generated in Sweden. It is distinct from residual mix, supplier mix and consumption intensity. The measure excludes biogenic CO₂ and lifecycle emissions. It is an estimate based on production shares and emission factors, not a measured national emissions inventory or a total for all greenhouse gases.

The [manifest](aib/manifest.json) records source URLs, retrieval dates and SHA-256 file fingerprints. Full reports and workbooks stay local; see [SOURCES.md](../../SOURCES.md) for restoration instructions and sharing terms.

[extract_aib_intensity.py](extract_aib_intensity.py) reads the selected reports and writes the [verified JSON extract](aib/sweden_production_co2_verified.json). [prepare_dashboard_co2_intensity.py](../../prepare_dashboard_co2_intensity.py) exports [dashboard_co2_intensity.csv](../../outputs/dashboard_co2_intensity.csv). It checks source fingerprints, years, country, production mix and values read back from the saved CSV.

| Year | Published g CO₂/kWh | PDF location |
|---|---:|---|
| 2015 | 13 | Figure 5, Production Mix row, SE column, p. 14 |
| 2016 | 14 | Table 5, SE row, p. 18 |
| 2017 | 12 | Table 5, SE row, p. 18 |
| 2018 | 12 | Table 5, SE row, p. 20 |
| 2019 | 11.89 | Table 5, SE row, p. 18 |
| 2020 | 5.67 | Table 5, SE row, p. 18 |
| 2021 | 7.67 | Table 5, SE row, p. 18 |
| 2022 | 6.62 | Table 5, SE row, p. 24 |
| 2023 | 6.52 | Table 5, SE row, p. 23 |
| 2024 | 5.05 | Table 5, SE row, p. 23 |

The 2022–2024 PDF values agree with the corresponding workbook Production Mix cells within 0.005 g CO₂/kWh. The series preserves the PDF precision: whole numbers for 2015–2018 and two decimal places thereafter. Extra workbook decimals are not substituted. The 2015, 2016 and 2024 report layouts were also checked visually.

## Method changes and document versions

- The series keeps each year's published values; it has not been recalculated with common emission factors. AIB changed from RE-DISS to Ecoinvent input factors from reporting year 2022. This does not mean every country's factor changed identically or that all other years use identical assumptions.
- Generation inputs also vary: earlier reports reference ENTSO-E, while later reports use national reporting and Eurostat. Changes in the series can reflect both production and method differences. A percentage reduction across the 2022 boundary cannot be treated as a verified physical emissions reduction.
- The [2024 landing page](https://www.aib-net.org/facts/european-residual-mix/2024) labels the publication version 2.0, but the linked corrected PDF identifies itself as version 1.1, dated 11 August 2025. The selected local file, `2024_0.pdf`, agrees with the linked workbook for Sweden's production mix. The 2017, 2018 and 2021 filenames also differ from their internal version labels. Identify versions from the documents and fingerprints, not filenames alone.
- A duplicate 2016 download URL returned 404 during collection. The working year-specific report was used; the failed URL remains in the manifest.
- AIB's 2019 residual-mix calculation change does not turn production-mix values into residual-mix values. The measures remain distinct.

Do not multiply these intensities by the separate SCB net-production totals to estimate annual tonnes, or derive them from Energimyndigheten's fossil-free shares. Compatible boundaries and generation denominators have not been established. Fossil-free generation can still release biogenic CO₂.

## Other sources considered

### SCB and Naturvårdsverket: electricity and district heating

The [SCB emissions table](https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__MI__MI0107/MI0107ELoFjarrNN/) offers CO₂, biogenic CO₂ and total greenhouse gases separately. It combines electricity with district heating, so its totals cannot be labelled electricity-only emissions. Biogenic CO₂ is separate from the inventory greenhouse-gas total, and CO₂ and CO₂ equivalents (CO₂e) are different measures. See also [Naturvårdsverket's explanation](https://www.naturvardsverket.se/data-och-statistik/klimat/vaxthusgaser-utslapp-fran-el-och-fjarrvarme/).

Section 8.4.3 of the [joint agency follow-up of electrification](https://energimyndigheten.a-w2m.se/Arkitektkopia/GetTemplateResource/121?eloid=04b90e827bd84cdea37ecdfabe133f93&elp=portal&elt=t&fn=Deluppdrag+1+-+myndighetsgemensam+uppf%C3%B6ljning+av+samh%C3%A4llets+elektrifiering.pdf&id=04b90e827bd84cdea37ecdfabe133f93&lr=False&res=97ed36ef0fa84344ba20c1fe2f50418b) confirms this combined reporting scope and points to AIB's annual production-mix intensity as an alternative. This supports the choice of intensity, but not a split of annual electricity-only tonnes into fossil and biogenic emissions.

### EEA: electricity-generation greenhouse-gas intensity

The [EEA indicator](https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1) estimates electricity-only emissions by allocating combined heat-and-power emissions and estimating emissions from producers generating for their own use. It reports g CO₂e/kWh using gross generation. Its convention assigns zero factors to renewables, including biomass; this does not mean biomass has no physical biogenic or lifecycle emissions.

The [country chart reviewed](https://www.eea.europa.eu/en/analysis/indicators/greenhouse-gas-emission-intensity-of-1/greenhouse-gas-emission-intensity-of-electricity-generation) showed selected years, not a verified Swedish 2015–2024 series of annual tonnes. Its gross-generation basis also prevents a direct conversion using this project's SCB net-generation totals.

### SCB and Energimyndigheten: fuel consumption

The [fuel-consumption table](https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__EN__EN0105__EN0105A/BrforelARb/) could support a separate estimate but is not an emissions series. The local research file `research/2026-10-20/TAB3125_en.csv` contains 2,080 records for 2015–2024: 8 plant labels × 26 fuel labels × 10 years, including 596 `..` entries. Their meaning must be checked before treating them as zero.

Plant and fuel labels include totals and subcategories, so summing every row would double count. Any emissions estimate would need verified category groupings, electricity/heat allocation, fossil fractions for mixed fuels, fuel-specific factors and coverage. Municipal waste, other fuels and surplus steam need particular attention. The source notes changes to wood-waste classification in 2022 and liquid biofuel classification in 2023.

### Other published sources

- [Ember yearly electricity data](https://ember-energy.org/data/yearly-electricity-data/) provides annual source-specific emissions but uses lifecycle factors, as described in its [methodology](https://files.ember-energy.org/public-downloads/ember_electricity_data_methodology.pdf). That scope differs from emissions during generation.
- [Energiföretagen's Energiåret 2024](https://www.energiforetagen.se/statistik/energiaret/energiaret-2024/) and its [March 2025 press release](https://www.mynewsdesk.com/se/energiforetagen/pressreleases/nytt-rekord-svensk-el-till-99-procent-fossilfri-3374961) provide generation, fuel and fossil-free-share statistics. The inspected material did not supply the required electricity-only annual fossil/biogenic CO₂ series. Preliminary generation shares are not emissions measurements.
- [Profu's electricity climate impacts for 2025](https://www.datocms-assets.com/106793/1773150061-klimatpaverkan-fran-elproduktion-och-anvandning-ar-2025-profu-2026-03-10.pdf), published 10 March 2026, mainly examines the consequences of changes in generation and consumption in northern Europe. It was not selected as a Swedish annual physical fossil/biogenic emissions dataset.

The source search did not establish a suitable annual-tonnage series; it does not show that none exists. Adding that measure would require an electricity-only source with documented coverage and heat allocation, or a separately labelled estimate with verified inputs. Fossil-free percentages and the label “other thermal generation” are not enough to calculate it.

## Dashboard presentation

The **CO₂ intensity** page uses annual columns titled **Sweden's direct CO₂ intensity of electricity production, 2015–2024**. Years run in ascending order, the Y-axis starts at zero and its unit is **g CO₂/kWh**. `Factor_period` distinguishes 2015–2021 from 2022–2024, with a note explaining the method change.

Use one intensity value per year; Average returns that value when there is one row. Do not sum intensities across years. The explanatory text should identify the AIB estimate, explain the exclusions and 2022 change, and distinguish intensity from annual totals or avoided emissions. See the [methods note](../../methods_note.md#direct-co₂-intensity) for the full interpretation and the [AIB reports](https://www.aib-net.org/facts/european-residual-mix) and [FAQ](https://www.aib-net.org/faq/residual-mix) for the source methodology.
