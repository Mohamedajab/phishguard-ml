import json
from pathlib import Path

import pandas as pd

from run_experiment import run


def test_experiment_evaluates_the_challenge_set(tmp_path: Path) -> None:
    summary = run(
        Path("data/messages.csv"),
        Path("data/challenge_messages.csv"),
        tmp_path,
    )

    assert summary["training_messages"] == 240
    assert summary["test_messages"] == 20

    saved_summary = json.loads((tmp_path / "metrics.json").read_text("utf-8"))
    predictions = pd.read_csv(tmp_path / "predictions.csv")

    assert saved_summary["f1"] == summary["f1"]
    assert len(predictions) == 20
    assert set(predictions["error_type"]) <= {
        "correct",
        "false_positive",
        "false_negative",
    }
