# Methodology and corrections

## Data provenance and calendar

The original course report identifies Carbon Monitor as the data source, gives emissions in MtCO₂/day and records 204,540 rows spanning 2019-01-01 to 2025-08-31. The bundled Excel workbook has four columns and the same row count. Its filename is not its final observation date.

The workbook mixes 123,900 DD/MM/YYYY strings with 80,640 Excel datetime cells. Ambiguous days 1–12 were converted with month and day reversed. In original row order, the August 2025 sequence contains `31/07/2025`, datetime `2025-01-08`, datetime `2025-02-08`, ... datetime `2025-12-08`, then text `13/08/2025`. Reading these datetimes literally moves observations to incorrect months.

`load_data` parses strings as DD/MM/YYYY and swaps month/day only for the native datetime cells in this particular workbook. It then requires the unique dates **in original row order** to equal a continuous daily calendar. The repaired dates agree with the report and yield 2,435 days through 2025-08-31. Every geography has all six sectors on every day, and there are no duplicate country/date/sector keys. The workbook itself is unchanged. Do not reuse this repair for a new data export without checking its format.

## Forecasting

- Sum sectors within a selected geography; never concatenate sector rows as time steps.
- Split raw dates chronologically: 70% training, 15% validation, 15% test (integer boundaries).
- Fit MinMaxScaler only on raw training values. Later values can exceed [0, 1].
- Build 30-day windows and assign samples according to target date. Past observations from the preceding split may be used as context; no target or future observation appears in its own input.
- Train a 64-unit LSTM, 0.2 dropout and a dense output, with Adam/MSE, batches of 32, no shuffling, seed 42 and deterministic TensorFlow operations. Stop on validation loss with patience five and restore the best weights, at most 30 epochs.
- Evaluate once on test dates with MAE/RMSE in MtCO₂/day. Persistence uses the prior observed day; seasonal naive uses the observed value seven days earlier. All three methods share the same dates and information horizon.
- The separate 30-step recursive extension starts after the last observed day, uses predicted values recursively and is not scored. The model/scaler are not refit on validation or test values.

This is one predefined evaluation, not hyperparameter tuning or evidence of universal model superiority. Test scores must not be used to tune the architecture repeatedly.

## Exploratory analysis

The country clustering excludes WORLD, ROW and EU27 & UK. Missing days are rejected rather than filled with zero. Date-wise standardisation across countries retains relative emissions magnitude. K-Means labels and Ward labels are separate outputs; neither is passed into the clustering feature matrix. Three clusters are illustrative rather than a proven optimum.

Symbolic sequences discretise overlapping 30-day rolling averages into five symbols. This resembles SAX but is not canonical non-overlapping PAA. The n-gram smoothing denominator includes all 5^n possible words. Rare-pattern flags are in-sample descriptive scores without ground-truth validation. No DTW code is present, so the earlier DTW claim has been removed.

CUSUM residual plots are exploratory. Autocorrelated, seasonal emissions can violate assumptions of a simple linear-trend residual test. The maximum cumulative residual location is not a confirmed breakpoint or evidence of causality. Centred moving averages are used only for retrospective visualisation, never as forecasting inputs.

## Historical results

The original notebook scaled the complete series before splitting and used test data for early stopping in its multi-geography loop. That loop also mixed sectors instead of aggregating daily totals. Historical scores are therefore not comparable with the corrected run. Original PDF/slides/PNG outputs are retained and explicitly labelled historical in the README.
