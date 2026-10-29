# Daily CO₂ Emissions: Data Mining and Forecasting

An academic team project exploring daily emissions across countries and sectors, with exploratory analysis, symbolic rare-pattern scoring, country clustering and LSTM forecasting. The reproducible workflow uses the bundled Carbon Monitor workbook and evaluates forecasting against simple baselines.

**Dataset:** 204,540 country-sector-day records, 2,435 days (1 January 2019–31 August 2025), six sectors and 14 geographies. Eleven are individual countries; WORLD, ROW and EU27 & UK are aggregates. Values are million tonnes of CO₂ per day (MtCO₂/day). Do not sum overlapping geographies.

## Start here

[Open in GitHub Codespaces](https://codespaces.new/Parisa6Izadyar/co2-emissions-data-mining?ref=improve%2Freproducible-co2-analysis)

Select the `improve/reproducible-co2-analysis` branch while this change is under review. The dev container installs Python dependencies; open `notebooks/co2_emissions_lstm_forecasting.ipynb`, select the Python kernel, and run all cells. Installation needs internet access; the default analysis then runs without API calls or credentials. CPU training is supported; no GPU is required. Codespaces configuration is provided, but a hosted Codespace has not been manually verified.

For local execution, use **Python 3.12** on Linux (the CI environment):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m co2_analysis --validate-only
python -m co2_analysis --countries WORLD Russia --epochs 30
```

On Windows use `.venv\Scripts\activate` instead. Other platforms are not covered by CI.

Open the notebook with `jupyter lab`. To execute it in a fresh kernel:

```bash
python -m ipykernel install --user --name python3
python scripts/execute_notebook.py --smoke
```

The smoke run executes the entire default notebook with one training epoch per geography to check integration. Omit `--smoke` for up to 30 epochs. Smoke-run scores are not benchmark results.

## What the project demonstrates

- Schema, duplicate, sector-coverage and daily-calendar validation on an Excel dataset.
- Sector and country comparisons, rolling trends and seasonal decomposition.
- Exploratory symbolic rare-pattern scoring and CUSUM diagnostics, with interpretation limits.
- K-Means and Ward clustering, keeping cluster labels separate from input features.
- LSTM forecasting with chronological train/validation/test partitions, training-only scaling, early stopping and baseline comparisons.
- Regression tests, a command-line workflow, notebook execution and GitHub Actions validation.

## Forecasting protocol

Aggregate the six sectors to one observation per geography per day. Split raw dates 70%/15%/15%; fit the scaler on training data only. Use the preceding 30 days to predict the next day. Validation selects the stopping epoch; test targets never train the model or select the epoch.

Report MAE and RMSE in original units for LSTM, previous-day persistence and seven-day seasonal-naive predictions on exactly the same test dates. These are **rolling one-day-ahead** results, not an evaluation of a fixed-origin 30-day forecast. The recursive future extension is illustrative and has no held-out outcome in this snapshot. A more complex model is not assumed to beat the baselines.

Run outputs go to `results/reproduced/`: per-day predictions, future extensions, comparison plots and `metrics.json` with dates, sample counts, software versions and the dataset checksum. See [methodology and corrections](docs/methodology.md) and [validation record](docs/validation.md). CI uploads its executed notebook and benchmark files as the `co2-evaluation` artifact.

## Files

| Path | Purpose |
| --- | --- |
| [Notebook](notebooks/co2_emissions_lstm_forecasting.ipynb) | Guided exploratory analysis and forecasting |
| `co2_analysis/` | Shared loading, validation and forecasting code |
| `tests/` | Regression checks for chronology, leakage and aggregation |
| [Dataset](data/carbonmonitor-global_datas_2025-10-07.xlsx) | Original bundled workbook; left unchanged |
| [Original report](report/DM%26ML_project-1_260924_001625.pdf) | Historical course submission |
| [Presentation](presentation/daily_co2_emissions_presentation.pptx) | Historical course slides |
| `results/*.png` | Historical plots; not regenerated benchmark evidence |

The report, slides and original figures predate the corrected workflow and can contain different code, metrics and interpretations. They are retained as course artifacts, not evidence for the corrected evaluation.

## Optional World Bank enrichment

The notebook's GDP/population section is disabled by default and is not needed for forecasting. Install `requirements-optional.txt`, set `RUN_WORLD_BANK = True` in the notebook, and rerun to request live World Bank indicators. Live values and availability can change; this optional path is not covered by the offline CI run.

## Context and limitations

The original report credits Francesco Stellato, Daniele Cavuto, Parisa Izadiyar and Aashi Sudhanshu Mehrotra, for the Data Mining & Machine Learning course (October 2025). This repository presents a team project, not sole authorship of all components.

Source attribution: [Carbon Monitor](https://carbonmonitor.org/), as documented in the original report. The workbook is an existing snapshot; this repository does not establish new redistribution rights. Emissions are estimates, not direct measurements. A single temporal holdout and one random seed do not establish generalisation across countries, regimes or model choices. Clustering and anomaly results are descriptive, with no labelled validation set or causal interpretation.
