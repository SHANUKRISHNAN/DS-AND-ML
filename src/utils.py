import pandas as pd
import numpy as np

TARGET = "co2_concentration_ppm"


def load_raw(path):
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise ValueError("Required column 'timestamp' is missing.")
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    if df["timestamp"].isna().any():
        bad = int(df["timestamp"].isna().sum())
        raise ValueError(f"Could not parse {bad} timestamp value(s). Check the date format.")
    return df


def add_time_features(df):
    out = df.copy()
    out["hour"] = out["timestamp"].dt.hour
    out["day"] = out["timestamp"].dt.day
    out["month"] = out["timestamp"].dt.month
    out["dayofweek"] = out["timestamp"].dt.dayofweek
    out["is_weekend"] = (out["dayofweek"] >= 5).astype(int)
    out["traffic_level"] = pd.cut(
        out["traffic_emission_rate_kg_h"],
        bins=[-np.inf, 200, 350, np.inf],
        labels=["Low", "Medium", "High"],
    ).astype(str)
    out["wind_category"] = pd.cut(
        out["wind_speed_ms"],
        bins=[-np.inf, 2, 5, np.inf],
        labels=["Low", "Medium", "High"],
    ).astype(str)
    return out
