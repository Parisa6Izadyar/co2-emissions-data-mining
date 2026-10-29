# Evaluation and testing

## Reproduce the checks

```bash
python -m pytest -q
python -m ipykernel install --user --name python3
python scripts/execute_notebook.py --smoke
python -m co2_analysis --countries WORLD Russia --epochs 30
```

The tests check daily and sector coverage, duplicate and missing records, aggregation, chronological splits and past-only input windows. Changing future observations must leave the training scaler and training samples unchanged.

The notebook smoke run executes all 48 cells with one epoch per geography. A separate benchmark trains for up to 30 epochs and evaluates each model on 366 test targets. CI also checks installation against `requirements-tested.txt`.

## Recorded benchmark

[Run 40971872716](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/runs/40971872716) passed on Ubuntu with Python 3.12.15. It executed the notebook and reproduced the rounded benchmark scores after installation with the tested dependency constraints.

The [full-precision summary](benchmark.json) was recorded from the preceding [run 40971380327](https://github.com/Parisa6Izadyar/co2-emissions-data-mining/actions/runs/40971380327), at the source commit named in that file. That run passed the 13 tests present at the time. WORLD trained for 30 epochs and Russia for 17; the seven-day baseline had the lowest WORLD errors, while persistence had the lowest Russia errors.

Both runs uploaded an executed notebook, four prediction CSVs, two evaluation plots and a metrics manifest. Download these from the `co2-evaluation` artifact on the run page. Artifacts follow GitHub's retention policy; the CLI regenerates the same file types from the bundled data.

## Coverage

GitHub Actions covers the default offline workflow. The live World Bank section and a hosted Codespaces session have not been tested. The dev container uses Python 3.12 and the recorded dependency constraints.
