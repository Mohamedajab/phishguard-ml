import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from phishguard.data import load_messages
from phishguard.evaluation import calculate_metrics
from phishguard.model import build_model, most_influential_terms


def run(data_path: Path, output_dir: Path) -> dict[str, object]:
    messages = load_messages(data_path)
    train, test = train_test_split(
        messages,
        test_size=0.25,
        random_state=42,
        stratify=messages["label"],
    )

    model = build_model()
    model.fit(train["text"], train["label"])
    predictions = model.predict(test["text"])
    probabilities = model.predict_proba(test["text"])[:, 1]

    metrics = calculate_metrics(test["label"].tolist(), predictions.tolist())
    phishing_terms, legitimate_terms = most_influential_terms(model)
    summary: dict[str, object] = {
        "dataset_size": len(messages),
        "training_messages": len(train),
        "test_messages": len(test),
        **metrics,
        "phishing_terms": phishing_terms,
        "legitimate_terms": legitimate_terms,
        "dataset_note": "Synthetic demonstration data; not a real-world performance claim.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(
        {
            "message_id": test["message_id"],
            "expected": test["label"],
            "predicted": predictions,
            "phishing_probability": probabilities.round(4),
        }
    ).to_csv(output_dir / "predictions.csv", index=False)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate the PhishGuard demo model")
    parser.add_argument("--data", type=Path, default=Path("data/messages.csv"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()

    result = run(args.data, args.output)
    print("PhishGuard evaluation")
    print(f"Messages: {result['dataset_size']} ({result['test_messages']} held out for testing)")
    print(f"Accuracy:  {result['accuracy']:.2%}")
    print(f"Precision: {result['precision']:.2%}")
    print(f"Recall:    {result['recall']:.2%}")
    print(f"F1:        {result['f1']:.2%}")
    print("\nSynthetic demo data only; validate on an external dataset before practical use.")


if __name__ == "__main__":
    main()

