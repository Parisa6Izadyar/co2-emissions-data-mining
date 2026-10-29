# Daily CO₂ Emissions

An academic team project using Carbon Monitor data to explore emissions trends, compare countries and evaluate daily forecasts. The analysis covers six sectors across 14 geographies from January 2019 to August 2025.

[CI results](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/workflows/tests.yml) · [Notebook](notebooks/co2_emissions_lstm_forecasting.ipynb) · [Methods](docs/methodology.md) · [Evaluation](docs/validation.md)

## Run the project

[Open in GitHub Codespaces](https://codespaces.new/Parisa6Izadyar/co2-emissions-data-mining?ref=main)

The dev container installs Python 3.12 and the tested dependencies. Once setup finishes, open `notebooks/co2_emissions_lstm_forecasting.ipynb`, select the Python kernel and run the cells in order.

To run the tests and forecasting workflow in the Codespaces terminal:

```bash
python -m pytest -q
python -m co2_analysis --countries WORLD Russia --epochs 30
```

Installation requires internet access. The default analysis then uses local data and runs on CPU without API keys.

### Local setup

The workflow is tested on Ubuntu with Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -c requirements-tested.txt
python -m pytest -q
python -m co2_analysis --validate-only
python -m co2_analysis --countries WORLD Russia --epochs 30
```

On Windows, activate the environment with `.venv\Scripts\activate`. Other operating systems are not covered by CI.

Use `jupyter lab` to open the notebook. For a fresh-kernel execution from the terminal:

```bash
python -m ipykernel install --user --name python3
python scripts/execute_notebook.py
```

Add `--smoke` for a one-epoch integration check. The benchmark uses up to 30 epochs per geography, with early stopping.

## Data and analysis

The bundled workbook contains **204,540 country-sector-day records** over **2,435 days**, from 1 January 2019 to 31 August 2025. Each record estimates emissions in million tonnes of CO₂ per day (MtCO₂/day). Eleven geographies are individual countries; WORLD, ROW and EU27 & UK are aggregates. Keep overlapping aggregates separate when comparing totals.

The notebook includes:

- Daily, monthly and sector-level comparisons, with seasonal decomposition.
- Rare symbolic pattern scores and CUSUM residual diagnostics for exploratory analysis.
- K-Means and Ward clustering of the 11 individual countries.
- LSTM forecasting for WORLD and Russia, compared with previous-day persistence and a seven-day seasonal-naive baseline.

The loader handles the workbook's mixed date formats and checks duplicate keys, calendar continuity and coverage of all six sectors. [Data and methods](docs/methodology.md) explains the date correction and the assumptions behind each analysis.

## Forecasting results

The model uses 30 observed days to predict the next day. Raw dates are split 70%/15%/15% for training, validation and test. Scaling uses training observations, and validation loss selects the stopping epoch. All three forecasting methods are evaluated on the same **366 test dates**, from 31 August 2024 to 31 August 2025.

| Geography | Model | MAE | RMSE |
| --- | --- | ---: | ---: |
| WORLD | LSTM | 2.7739 | 3.3806 |
| WORLD | Previous-day persistence | 2.7185 | 3.4115 |
| WORLD | Seven-day seasonal naive | **2.5474** | **3.3748** |
| Russia | LSTM | 0.1266 | 0.1679 |
| Russia | Previous-day persistence | **0.0988** | **0.1266** |
| Russia | Seven-day seasonal naive | 0.1619 | 0.2222 |

Errors are in MtCO₂/day; lower is better. The seven-day baseline performed best for WORLD, and persistence performed best for Russia. The LSTM trained for 30 and 17 epochs respectively. These results come from one temporal split and seed 42; they provide a baseline comparison for this experiment.

Test predictions are made one day at a time, using observations available before each target date. The separate 30-day recursive extension starts after the last observation and has no measured outcomes in this snapshot.

[Full-precision benchmark](docs/benchmark.json) · [Verified run](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/runs/40974223226)

### Generated outputs

A CLI run writes to `results/reproduced/`:

- `world_test.csv` and `russia_test.csv`: observed values and all three predictions by date.
- `world_future.csv` and `russia_future.csv`: illustrative recursive extensions.
- `world_evaluation.png` and `russia_evaluation.png`: test predictions and training curves.
- `metrics.json`: errors, split dates, sample counts, software versions and dataset checksum.

Notebook outputs are written separately to `results/notebook/`. CI uploads its executed notebook and benchmark files as the `co2-evaluation` artifact. Use `requirements-tested.txt` to install the recorded dependency versions; small numerical differences across hardware are possible.

## Repository files

| Path | Contents |
| --- | --- |
| `co2_analysis/` | Data validation, chronological splits and forecasting |
| `notebooks/` | Exploration and forecasting notebook |
| `tests/` | Regression checks for data quality, aggregation and chronology |
| [Workbook](data/carbonmonitor-global_datas_2025-10-07.xlsx) | Bundled Carbon Monitor snapshot |
| [Course report](report/DM%26ML_project-1_260924_001625.pdf) | Original October 2025 submission |
| [Presentation](presentation/daily_co2_emissions_presentation.pptx) | Original course slides |
| `results/*.png` | Figures from the original course analysis |

The report, slides and original figures document the course submission. Use the current workflow and benchmark for the revised forecasting evaluation.

## Optional population and GDP data

Install `requirements-optional.txt` and set `RUN_WORLD_BANK = True` in the notebook to retrieve World Bank indicators. This section compares complete years through 2024. It is separate from the default forecasting workflow, and live API values may change.

## Project context

The original report credits Francesco Stellato, Daniele Cavuto, Parisa Izadiyar and Aashi Sudhanshu Mehrotra, for the Data Mining & Machine Learning course in October 2025. Data source: [Carbon Monitor](https://carbonmonitor.org/), as cited in that report.

Clustering and rare-pattern scores describe the observed dataset. They have no labelled validation set. CUSUM results also depend on assumptions about seasonality and residual dependence; the notebook treats them as exploratory diagnostics.
