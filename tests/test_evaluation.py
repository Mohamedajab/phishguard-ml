from phishguard.evaluation import calculate_metrics


def test_metrics_include_confusion_matrix_counts() -> None:
    result = calculate_metrics([0, 0, 1, 1], [0, 1, 1, 1])

    assert result["true_positive"] == 2
    assert result["true_negative"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 0
    assert result["recall"] == 1.0

