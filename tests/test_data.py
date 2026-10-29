import pandas as pd
import pytest
from co2_analysis.data import load_data, daily_series, validate_data


@pytest.fixture(scope="module")
def data():
    return load_data()


def test_snapshot_calendar_and_shape(data):
    assert len(data) == 204540
    assert data.date.nunique() == 2435
    assert data.date.min() == pd.Timestamp("2019-01-01")
    assert data.date.max() == pd.Timestamp("2025-08-31")
    assert data.country.nunique() == 14
    assert data.sector.nunique() == 6


def test_sector_aggregation_produces_one_value_per_day(data):
    result = daily_series(data, "Russia")
    assert len(result) == 2435
    assert result.index.is_unique
    assert result.iloc[0] == pytest.approx(data.loc[(data.country == "Russia") & (data.date == result.index[0]), "value"].sum())


def test_duplicate_rows_rejected(data):
    with pytest.raises(ValueError, match="Duplicate"):
        validate_data(pd.concat([data, data.iloc[:1]]))


def test_missing_sector_rejected(data):
    with pytest.raises(ValueError, match="sector"):
        validate_data(data.iloc[1:])


def test_unknown_country_rejected(data):
    with pytest.raises(ValueError, match="Unknown"):
        daily_series(data, "Unknown")
