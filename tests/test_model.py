from phishguard.model import build_model, most_influential_terms


def test_model_trains_and_returns_probabilities() -> None:
    text = [
        "team meeting notes attached",
        "library reminder no action needed",
        "verify password immediately urgent",
        "claim reward enter payment details",
    ]
    labels = [0, 0, 1, 1]
    model = build_model()
    model.fit(text, labels)

    probabilities = model.predict_proba(["urgent password verification"])[0]
    assert len(probabilities) == 2
    assert 0 <= probabilities[1] <= 1

    phishing, legitimate = most_influential_terms(model, count=2)
    assert len(phishing) == 2
    assert len(legitimate) == 2

