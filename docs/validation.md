# Validation record

## Verified GitHub Actions execution

[Run 40971380327](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/runs/40971380327) passed on Ubuntu / Python 3.12.15 at source commit `d9b81da5d606abe2892097ba39769a7279d1bdae`:

- 13 regression tests passed (9.28 seconds in CI).
- All 48 notebook cells executed in a fresh kernel, using one epoch per geography as an integration smoke test. Optional live World Bank enrichment remained disabled.
- The separate full benchmark completed: WORLD trained for 30 epochs and Russia for 17 with early stopping; both were evaluated on 366 test targets.
- Eight generated files were uploaded: the executed notebook, four prediction/extension CSVs, two evaluation plots and the metrics manifest.

[Download that run's artifact](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/runs/40971380327/artifacts/12940880633). GitHub artifacts are subject to retention limits; the [checked-in benchmark summary](benchmark.json) preserves the numeric results copied from the job log and identifies their source commit. Rerun the CLI to regenerate the full outputs.

Tests cover the repaired calendar, daily aggregation, missing sector and duplicate rejection, disjoint target dates, past-only windows and invariance of training inputs/scaler to future data changes. The full run evaluates the model without asserting that it must beat a baseline. It does not: seven-day seasonal naive performs best for WORLD and persistence performs best for Russia in both reported metrics.

## Local and unverified paths

The 13 tests, notebook schema validation and default exploratory code cells also passed locally. Local TensorFlow training and Jupyter kernel execution were attempted but blocked by execution-sandbox restrictions (executable-path lookup and socket/interface access); successful model/notebook execution was verified in GitHub Actions instead.

The optional live World Bank path and hosted Codespaces session have not been verified. Codespaces includes the same Python major/minor version and tested dependency constraints used for CI.
