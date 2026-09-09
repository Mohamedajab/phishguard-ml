from pathlib import Path

import numpy as np
import pytest
from sklearn.model_selection import StratifiedGroupKFold

from phishguard.data import load_messages, reject_overlap
from phishguard.model import build_model, most_influential_terms
from research import training_groups, choose_threshold, run


def test_groups_never_cross_folds():
    frame = load_messages(Path("data/messages.csv"))
    groups = training_groups(frame)
    assert len(set(groups)) == 16
    for fit, valid in StratifiedGroupKFold(4).split(frame.text, frame.label, groups):
        assert not set(groups[fit]) & set(groups[valid])


def test_overlap_rejected():
    frame = load_messages(Path("data/challenge_messages.csv"))
    with pytest.raises(ValueError, match="overlapping"):
        reject_overlap(frame, frame.copy())


def test_threshold_analysis():
    threshold, rows = choose_threshold([0, 0, 1, 1], np.array([0.1, 0.2, 0.8, 0.9]))
    assert threshold == 0.5
    assert len(rows) == 17


def test_character_features():
    assert build_model("char").named_steps["tfidf"].analyzer == "char_wb"
    with pytest.raises(ValueError):
        build_model("unknown")
    with pytest.raises(ValueError):
        most_influential_terms(build_model(), 0)


def test_external_mapping(tmp_path):
    path = tmp_path / "external.csv"
    path.write_text("id,title,message,target,group\n1,Hello,Meeting,ham,a\n2,Warning,Enter password,spam,b\n")
    frame = load_messages(path, {"id": "message_id", "title": "subject", "message": "body", "target": "label"}, {"ham": 0, "spam": 1})
    assert frame.label.tolist() == [0, 1]
    assert training_groups(frame).tolist() == ["a", "b"]


def test_research_saves_both_models_without_test_tuning(tmp_path):
    import pandas as pd
    rows = [{"message_id": str(i), "subject": "Notice", "body": f"{'meeting notes' if i % 2 == 0 else 'verify password'} {i}",
             "label": i % 2, "group": f"campaign-{i}"} for i in range(24)]
    train = tmp_path / "train.csv"
    test = tmp_path / "test.csv"
    pd.DataFrame(rows).to_csv(train, index=False)
    pd.DataFrame([{**rows[0], "body": "seminar at noon", "group": "test-a"},
                  {**rows[1], "body": "supply bank password", "group": "test-b"}]).to_csv(test, index=False)
    result = run(train, test, tmp_path / "result")
    assert len(result["models"]) == 2
    assert all(len(model["cv_fold_f1_at_0_5"]) == 4 for model in result["models"])
    assert len(pd.read_csv(tmp_path / "result/folds.csv")) == 48
