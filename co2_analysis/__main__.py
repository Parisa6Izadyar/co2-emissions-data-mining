"""Run a reproducible benchmark from the repository root."""
import argparse
import json
from pathlib import Path
import platform
from importlib.metadata import version

from .data import load_data, daily_series, data_summary
from .forecast import fit_forecast


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", nargs="+", default=["WORLD", "Russia"])
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("results/reproduced"))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    frame = load_data()
    summary = data_summary(frame)
    print(json.dumps(summary, indent=2))
    if args.validate_only:
        return
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"data": summary, "python": platform.python_version(),
              "packages": {p: version(p) for p in ["tensorflow-cpu", "numpy", "pandas", "scikit-learn"]},
              "evaluation": "rolling one-day-ahead; no test targets used in training or early stopping",
              "countries": {}}
    for country in args.countries:
        predictions, forecast, metadata, history = fit_forecast(daily_series(frame, country), epochs=args.epochs)
        slug = country.lower().replace(" ", "_")
        predictions.to_csv(args.output / f"{slug}_test.csv", index=False)
        forecast.to_csv(args.output / f"{slug}_future.csv", index=False)
        report["countries"][country] = metadata
        (args.output / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 1, figsize=(11, 7), layout="constrained")
        predictions.set_index("date")[["actual", "lstm", "seasonal_naive_7"]].plot(ax=axes[0])
        axes[0].set(title=f"{country}: rolling one-day-ahead test predictions", ylabel="MtCO2/day")
        axes[1].plot(history["loss"], label="train")
        axes[1].plot(history["val_loss"], label="validation")
        axes[1].set(xlabel="Epoch (zero-based)", ylabel="Scaled MSE")
        axes[1].legend()
        fig.savefig(args.output / f"{slug}_evaluation.png", dpi=140)
        plt.close(fig)
        print(country, json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
