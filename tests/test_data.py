from pathlib import Path

import pandas as pd
import pytest

from phishguard.data import load_messages


def test_loader_combines_subject_and_body(tmp_path: Path) -> None:
    path = tmp_path / "messages.csv"
    pd.DataFrame(
        [
            {"message_id": "a", "subject": "Hello", "body": "Meeting at ten", "label": 0},
            {"message_id": "b", "subject": "Urgent", "body": "Confirm password", "label": 1},
        ]
    ).to_csv(path, index=False)

    messages = load_messages(path)
    assert messages.loc[0, "text"] == "Hello Meeting at ten"


def test_loader_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame([{"body": "Only one column"}]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing columns"):
        load_messages(path)


def test_challenge_set_has_both_classes() -> None:
    messages = load_messages(Path("data/challenge_messages.csv"))

    assert len(messages) == 20
    assert messages["label"].value_counts().to_dict() == {0: 10, 1: 10}
