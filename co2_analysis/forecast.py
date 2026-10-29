"""Chronological LSTM evaluation with explicit validation and naive baselines."""
from dataclasses import dataclass
import os

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


@dataclass
class Split:
    scaler: MinMaxScaler
    x: np.ndarray
    y: np.ndarray
    dates: pd.DatetimeIndex
    train: np.ndarray
    validation: np.ndarray
    test: np.ndarray
    train_end: int
    validation_end: int
    scaled: np.ndarray


def prepare(series, window=30, train_fraction=0.70, validation_fraction=0.15):
    """Split by target date and fit the scaler only on raw training observations.

    Earlier observed values may appear in later input windows. This models
    rolling one-day-ahead predictions, not a fixed-origin multi-day forecast.
    """
    if window < 7 or not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("Use window >= 7 and positive split fractions below one")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Leave a nonempty test partition")
    dates = pd.DatetimeIndex(series.index)
    if not dates.equals(pd.date_range(dates.min(), dates.max(), freq="D")):
        raise ValueError("Series must have unique, ordered, consecutive daily dates")
    values = series.to_numpy(dtype=float).reshape(-1, 1)
    if not np.isfinite(values).all():
        raise ValueError("Non-finite observations")
    train_end = int(len(values) * train_fraction)
    validation_end = int(len(values) * (train_fraction + validation_fraction))
    if train_end <= window or validation_end <= train_end or validation_end >= len(values):
        raise ValueError("Not enough observations for the requested window and splits")
    scaler = MinMaxScaler().fit(values[:train_end])
    scaled = scaler.transform(values).astype(np.float32)
    targets = np.arange(window, len(values))
    x = np.stack([scaled[i-window:i] for i in targets])
    y = scaled[targets]
    return Split(scaler, x, y, dates[targets], targets < train_end,
                 (targets >= train_end) & (targets < validation_end),
                 targets >= validation_end, train_end, validation_end, scaled)


def errors(actual, predicted):
    difference = np.asarray(actual).ravel() - np.asarray(predicted).ravel()
    return {"mae": float(np.mean(np.abs(difference))),
            "rmse": float(np.sqrt(np.mean(difference ** 2)))}


def fit_forecast(series, epochs=30, window=30, seed=42, horizon=30):
    if epochs < 1 or horizon < 1:
        raise ValueError("epochs and horizon must be positive")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
    os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")
    import tensorflow as tf

    tf.keras.backend.clear_session()
    tf.keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()
    split = prepare(series, window)

    def batches(mask):
        dataset = tf.data.Dataset.from_tensor_slices((split.x[mask], split.y[mask]))
        options = tf.data.Options()
        options.threading.private_threadpool_size = 1
        return dataset.batch(32).with_options(options)

    model = tf.keras.Sequential([
        tf.keras.Input(shape=(window, 1)), tf.keras.layers.LSTM(64),
        tf.keras.layers.Dropout(0.2), tf.keras.layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    history = model.fit(
        batches(split.train), validation_data=batches(split.validation),
        epochs=epochs, shuffle=False, verbose=0,
        callbacks=[tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True)],
    )
    prediction = split.scaler.inverse_transform(
        model(split.x[split.test], training=False).numpy()).ravel()
    positions = np.flatnonzero(split.test) + window
    raw = series.to_numpy()
    predictions = pd.DataFrame({
        "date": split.dates[split.test], "actual": raw[positions],
        "lstm": prediction, "persistence": raw[positions-1],
        "seasonal_naive_7": raw[positions-7],
    })
    metrics = {name: errors(predictions.actual, predictions[name])
               for name in ["lstm", "persistence", "seasonal_naive_7"]}
    sequence = split.scaled[-window:].copy()
    future = []
    for _ in range(horizon):
        value = float(model(sequence[None, ...], training=False).numpy()[0, 0])
        future.append(value)
        sequence = np.concatenate([sequence[1:], [[value]]]).astype(np.float32)
    forecast = pd.DataFrame({
        "date": pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon),
        "lstm": split.scaler.inverse_transform(np.array(future).reshape(-1, 1)).ravel(),
    })
    metadata = {
        "seed": seed, "window_days": window, "epochs_requested": epochs,
        "epochs_run": len(history.history["loss"]),
        "train_end": str(series.index[split.train_end-1].date()),
        "validation_start": str(series.index[split.train_end].date()),
        "validation_end": str(series.index[split.validation_end-1].date()),
        "test_start": str(series.index[split.validation_end].date()),
        "test_end": str(series.index[-1].date()),
        "train_targets": int(split.train.sum()),
        "validation_targets": int(split.validation.sum()), "test_targets": int(split.test.sum()),
        "metrics": metrics,
    }
    return predictions, forecast, metadata, history.history
