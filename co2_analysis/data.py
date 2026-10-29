"""Load the bundled workbook without depending on Colab or remote APIs."""
from datetime import datetime
from pathlib import Path
import hashlib

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/carbonmonitor-global_datas_2025-10-07.xlsx"
AGGREGATES = {"WORLD", "ROW", "EU27 & UK"}


def load_data(path=DATA_PATH):
    """Repair this workbook's mixed Excel/text dates, then validate its daily grid.

    Excel converted ambiguous DD/MM dates to MM/DD datetimes. Text dates
    (days 13 onward) retain DD/MM/YYYY. Reversing the datetime month/day
    restores the original row order to one uninterrupted daily sequence.
    This is a snapshot-specific repair, not a general Excel date parser.
    """
    frame = pd.read_excel(path, sheet_name="in")
    required = {"country", "date", "sector", "value"}
    if set(frame.columns) != required:
        raise ValueError(f"Expected columns {sorted(required)}")
    if frame.isna().any().any():
        raise ValueError("Missing values in source workbook")

    def repair(value):
        if isinstance(value, datetime):
            return datetime(value.year, value.day, value.month)
        return datetime.strptime(value, "%d/%m/%Y")

    frame["date"] = pd.to_datetime(frame["date"].map(repair))
    observed = pd.DatetimeIndex(frame["date"].drop_duplicates())
    expected = pd.date_range(observed.min(), observed.max(), freq="D")
    if not observed.equals(expected):
        raise ValueError("Workbook date repair did not recover a continuous ordered calendar")
    validate_data(frame)
    return frame.sort_values(["country", "date", "sector"]).reset_index(drop=True)


def validate_data(frame):
    if frame.duplicated(["country", "date", "sector"]).any():
        raise ValueError("Duplicate country/date/sector records")
    if not np.isfinite(frame["value"]).all() or (frame["value"] < 0).any():
        raise ValueError("Emissions must be finite and nonnegative")
    sectors = set(frame["sector"].unique())
    for country, group in frame.groupby("country"):
        dates = pd.DatetimeIndex(group["date"].unique()).sort_values()
        if not dates.equals(pd.date_range(dates.min(), dates.max(), freq="D")):
            raise ValueError(f"Missing daily observations for {country}")
        if not group.groupby("date")["sector"].nunique().eq(len(sectors)).all():
            raise ValueError(f"Incomplete sector coverage for {country}")


def daily_series(frame, country):
    """Sum sectors within one geography; never add WORLD to its components."""
    selected = frame.loc[frame["country"].eq(country)]
    if selected.empty:
        raise ValueError(f"Unknown geography: {country}")
    validate_data(selected)
    series = selected.groupby("date")["value"].sum().sort_index()
    series.name = country
    return series


def data_summary(frame, path=DATA_PATH):
    return {
        "rows": len(frame), "geographies": frame.country.nunique(),
        "sectors": frame.sector.nunique(), "days": frame.date.nunique(),
        "start": str(frame.date.min().date()), "end": str(frame.date.max().date()),
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
    }
