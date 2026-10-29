import numpy as np
import pandas as pd
import pytest
from co2_analysis.forecast import prepare, errors


def series():
    return pd.Series(np.arange(200, dtype=float), index=pd.date_range("2020-01-01", periods=200))


def test_future_values_cannot_change_training_scaler_or_windows():
    original = series()
    changed = original.copy()
    changed.iloc[140:] = 100000
    a, b = prepare(original), prepare(changed)
    np.testing.assert_array_equal(a.scaler.data_max_, [139])
    np.testing.assert_array_equal(a.scaler.data_max_, b.scaler.data_max_)
    np.testing.assert_array_equal(a.x[a.train], b.x[b.train])
    np.testing.assert_array_equal(a.y[a.train], b.y[b.train])
    assert b.scaled[-1, 0] > 1  # Future extremes must not be clipped or fitted.


def test_target_dates_are_disjoint_and_windows_use_only_past():
    raw = series()
    split = prepare(raw)
    assert (split.train.astype(int) + split.validation + split.test == 1).all()
    assert split.dates[split.train].max() < split.dates[split.validation].min()
    assert split.dates[split.validation].max() < split.dates[split.test].min()
    for i, date in enumerate(split.dates):
        expected = raw.loc[:date].iloc[-31:-1].to_numpy()
        actual = split.scaler.inverse_transform(split.x[i]).ravel()
        np.testing.assert_allclose(actual, expected, atol=2e-5)


@pytest.mark.parametrize("kind", ["gap", "duplicate", "reverse", "nan"])
def test_invalid_series_is_rejected(kind):
    raw = series()
    if kind == "gap": raw = raw.drop(raw.index[50])
    if kind == "duplicate": raw.index = [raw.index[0]] * len(raw)
    if kind == "reverse": raw = raw.iloc[::-1]
    if kind == "nan": raw.iloc[20] = np.nan
    with pytest.raises(ValueError): prepare(raw)


def test_metrics_in_original_units():
    assert errors([1, 3], [2, 2]) == {"mae": 1.0, "rmse": 1.0}


def test_short_series_rejected():
    with pytest.raises(ValueError): prepare(series().iloc[:35])
