from typing import Any

from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


def calculate_metrics(expected: list[int], predicted: list[int]) -> dict[str, Any]:
    """Calculate classification scores and confusion-matrix counts."""
    precision, recall, f1, _ = precision_recall_fscore_support(
        expected, predicted, average="binary", zero_division=0
    )
    true_negative, false_positive, false_negative, true_positive = confusion_matrix(
        expected, predicted, labels=[0, 1]
    ).ravel()

    return {
        "accuracy": round(float(accuracy_score(expected, predicted)), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "true_positive": int(true_positive),
        "true_negative": int(true_negative),
        "false_positive": int(false_positive),
        "false_negative": int(false_negative),
    }

