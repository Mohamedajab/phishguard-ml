import argparse
import json
from pathlib import Path

import pandas as pd

from phishguard.data import load_messages
from phishguard.evaluation import calculate_metrics
from phishguard.model import build_model, most_influential_terms


def run(
    training_path: Path,
    challenge_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    train = load_messages(training_path)
    test = load_messages(challenge_path)
    model = build_model()
    model.fit(train["text"], train["label"])
    predictions = model.predict(test["text"])
    probabilities = model.predict_proba(test["text"])[:, 1]

    metrics = calculate_metrics(test["label"].tolist(), predictions.tolist())
    phishing_terms, legitimate_terms = most_influential_terms(model)
    summary: dict[str, object] = {
        "dataset_size": len(train) + len(test),
        "training_messages": len(train),
        "test_messages": len(test),
        **metrics,
        "phishing_terms": phishing_terms,
        "legitimate_terms": legitimate_terms,
        "dataset_note": (
            "Model trained on generated examples and evaluated on a separate "
            "hand-written challenge set. Results are not a real-world performance claim."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(
        {
            "message_id": test["message_id"],
            "subject": test["subject"],
            "expected": test["label"],
            "predicted": predictions,
            "phishing_probability": probabilities.round(4),
            "error_type": [
                "correct"
                if expected == predicted
                else "false_positive"
                if predicted == 1
                else "false_negative"
                for expected, predicted in zip(test["label"], predictions)
            ],
        }
    ).to_csv(output_dir / "predictions.csv", index=False)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate PhishGuard")
    parser.add_argument("--training", type=Path, default=Path("data/messages.csv"))
    parser.add_argument(
        "--challenge",
        type=Path,
        default=Path("data/challenge_messages.csv"),
    )
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()

    result = run(args.training, args.challenge, args.output)
    print("PhishGuard evaluation")
    print(f"Training messages: {result['training_messages']}")
    print(f"Challenge messages: {result['test_messages']}")
    print(f"Accuracy:  {result['accuracy']:.2%}")
    print(f"Precision: {result['precision']:.2%}")
    print(f"Recall:    {result['recall']:.2%}")
    print(f"F1:        {result['f1']:.2%}")
    print("\nSynthetic demo data only; validate on an external dataset before practical use.")


if __name__ == "__main__":
    main()
