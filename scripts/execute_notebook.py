"""Execute all notebook cells in a fresh kernel; optionally reduce training to one epoch."""
import argparse
import os
from pathlib import Path
import nbformat
from nbclient import NotebookClient

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--smoke", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
if args.smoke:
    os.environ["CO2_EPOCHS"] = "1"
path = root / "notebooks/co2_emissions_lstm_forecasting.ipynb"
notebook = nbformat.read(path, as_version=4)
NotebookClient(notebook, timeout=1200, kernel_name="python3", resources={"metadata": {"path": str(root)}}).execute()
output = path.with_suffix(".executed.ipynb")
nbformat.write(notebook, output)
print(f"Executed {len(notebook.cells)} cells: {output}")
