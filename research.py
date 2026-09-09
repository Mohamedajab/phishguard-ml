"""Training-only model/threshold selection followed by fixed challenge evaluation."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from importlib.metadata import version

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedGroupKFold

from phishguard.data import load_messages, reject_overlap
from phishguard.evaluation import calculate_metrics
from phishguard.model import build_model
from scripts.build_demo_dataset import SAFE_BODIES, PHISH_BODIES

ROOT = Path(__file__).resolve().parent


def training_groups(frame):
    if "group" in frame:
        if frame.group.isna().any():
            raise ValueError("group cannot contain missing values")
        return frame.group.astype(str).to_numpy()
    templates = SAFE_BODIES + PHISH_BODIES
    patterns = [re.compile(re.sub(r"\\\{\w+\\\}", ".+?", re.escape(t))) for t in templates]
    groups = []
    for body in frame.body:
        matches = [i for i, pattern in enumerate(patterns) if pattern.fullmatch(body)]
        if len(matches) != 1:
            raise ValueError("External training data requires a group column (campaign, sender or source)")
        groups.append(f"body-template-{matches[0]}")
    return np.array(groups)


def choose_threshold(labels, probabilities):
    candidates = np.linspace(0.1, 0.9, 17)
    rows = [{"threshold": float(t), **calculate_metrics(labels, (probabilities >= t).astype(int))} for t in candidates]
    best = max(rows, key=lambda row: (row["f1"], -abs(row["threshold"] - 0.5)))
    return best["threshold"], rows


def run(training, challenge, output, column_map=None, label_map=None):
    train = load_messages(training, column_map, label_map)
    test = load_messages(challenge, column_map, label_map)
    reject_overlap(train, test)
    groups = training_groups(train)
    splits = list(StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=42).split(train.text, train.label, groups))
    for fit, valid in splits:
        if set(groups[fit]) & set(groups[valid]) or train.label.iloc[fit].nunique() != 2 or train.label.iloc[valid].nunique() != 2:
            raise ValueError("Invalid group split: use more balanced campaign groups")
    output.mkdir(parents=True, exist_ok=True)
    reports, predictions, thresholds, curves, folds = [], [], [], [], []
    for features in ("word", "char"):
        oof = np.zeros(len(train))
        fold_scores = []
        for fold, (fit, valid) in enumerate(splits):
            model = build_model(features)
            model.fit(train.text.iloc[fit], train.label.iloc[fit])
            oof[valid] = model.predict_proba(train.text.iloc[valid])[:, 1]
            fold_scores.append(float(f1_score(train.label.iloc[valid], oof[valid] >= 0.5)))
            folds.extend({"message_id": train.message_id.iloc[i], "group": groups[i], "fold": fold, "features": features, "probability": float(oof[i])} for i in valid)
        threshold, analysis = choose_threshold(train.label, oof)
        thresholds.extend({"features": features, **row} for row in analysis)
        model = build_model(features).fit(train.text, train.label)
        probability = model.predict_proba(test.text)[:, 1]
        predicted = (probability >= threshold).astype(int)
        reports.append({"features": features, "threshold": threshold,
                        "cv_fold_f1_at_0_5": fold_scores, "cv_mean_f1": float(np.mean(fold_scores)),
                        "cv_std_f1": float(np.std(fold_scores, ddof=1)),
                        "challenge": calculate_metrics(test.label, predicted),
                        "roc_auc": float(roc_auc_score(test.label, probability)),
                        "average_precision": float(average_precision_score(test.label, probability))})
        fpr, tpr, _ = roc_curve(test.label, probability)
        precision, recall, _ = precision_recall_curve(test.label, probability)
        curves.extend({"features": features, "curve": "ROC", "x": float(x), "y": float(y)} for x, y in zip(fpr, tpr))
        curves.extend({"features": features, "curve": "PR", "x": float(x), "y": float(y)} for x, y in zip(recall, precision))
        for i, row in test.reset_index(drop=True).iterrows():
            error = "correct" if row.label == predicted[i] else ("false_positive" if predicted[i] else "false_negative")
            predictions.append({"features": features, "message_id": row.message_id, "subject": row.subject,
                                "text": row.text, "actual": row.label, "predicted": int(predicted[i]),
                                "probability": float(probability[i]), "error": error})
    selected = max(reports, key=lambda report: report["cv_mean_f1"])["features"]
    result = {"models": reports, "selected_by_training_cv": selected,
              "training_sha256": hashlib.sha256(training.read_bytes()).hexdigest(),
              "challenge_sha256": hashlib.sha256(challenge.read_bytes()).hexdigest(),
              "training_n": len(train), "challenge_n": len(test), "seed": 42,
              "packages": {name: version(name) for name in ("numpy", "pandas", "scikit-learn")},
              "note": "Body-template grouped CV; subject templates still recur. Thresholds selected from training OOF only. CV is selection evidence, not an unbiased final estimate. Challenge synthetic and previously inspected."}
    (output / "research.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, rows in [("predictions", predictions), ("thresholds", thresholds), ("curves", curves), ("folds", folds)]:
        pd.DataFrame(rows).to_csv(output / f"{name}.csv", index=False)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=ROOT / "data/messages.csv")
    parser.add_argument("--challenge", type=Path, default=ROOT / "data/challenge_messages.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results/research")
    parser.add_argument("--schema", type=Path, help='JSON with column_map and label_map; mappings apply to both files')
    args = parser.parse_args()
    schema = json.loads(args.schema.read_text("utf-8")) if args.schema else {}
    print(json.dumps(run(args.training, args.challenge, args.output, **schema), indent=2))
