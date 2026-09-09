from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"message_id", "subject", "body", "label"}


def load_messages(path: str | Path) -> pd.DataFrame:
    """Load and validate the labelled email dataset."""
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    if frame.empty:
        raise ValueError("Dataset contains no messages")

    labels = set(frame["label"].unique())
    if labels != {0, 1}:
        raise ValueError("Labels must contain both 0 (legitimate) and 1 (phishing)")

    frame = frame.copy()
    frame["text"] = (
        frame["subject"].fillna("").str.strip()
        + " "
        + frame["body"].fillna("").str.strip()
    ).str.strip()
    return frame

