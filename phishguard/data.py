from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"message_id", "subject", "body", "label"}


def load_messages(path: str | Path, column_map: dict | None = None, label_map: dict | None = None) -> pd.DataFrame:
    """Load and validate the labelled email dataset."""
    frame = pd.read_csv(path)
    if column_map:
        frame = frame.rename(columns=column_map)
    if label_map:
        frame["label"] = frame["label"].map(label_map)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    if frame.empty:
        raise ValueError("Dataset contains no messages")
    if frame["message_id"].isna().any() or frame["message_id"].duplicated().any():
        raise ValueError("message_id must be non-null and unique")

    labels = set(frame["label"].unique())
    if labels != {0, 1}:
        raise ValueError("Labels must contain both 0 (legitimate) and 1 (phishing)")

    frame = frame.copy()
    frame["text"] = (
        frame["subject"].fillna("").str.strip()
        + " "
        + frame["body"].fillna("").str.strip()
    ).str.strip()
    if frame["text"].eq("").any():
        raise ValueError("Messages cannot be empty")
    return frame


def reject_overlap(train: pd.DataFrame, test: pd.DataFrame) -> None:
    normalise = lambda series: series.str.casefold().str.replace(r"\s+", " ", regex=True).str.strip()
    if set(normalise(train.text)) & set(normalise(test.text)):
        raise ValueError("Training and evaluation contain overlapping messages")
    if "group" in train and "group" in test and set(train.group) & set(test.group):
        raise ValueError("Training and evaluation share groups")
