# Validation record

The local data and chronology suite passes 13 tests. It checks the repaired calendar, daily aggregation, missing sector and duplicate rejection, disjoint target dates, past-only windows and invariance of training inputs/scaler to future data changes.

Local TensorFlow training and Jupyter kernel execution were attempted but were blocked by the execution sandbox (TensorFlow executable-path lookup and Jupyter socket/interface access). They are not claimed as successful local runs. GitHub Actions runs the same tests, a fresh-kernel notebook smoke test and the 30-epoch-cap WORLD/Russia benchmark on Ubuntu/Python 3.12. CI status and measured results are recorded after that run completes.

The optional live World Bank path and hosted Codespaces session have not been verified. Codespaces includes configuration for the same Python version and dependencies used in CI.
