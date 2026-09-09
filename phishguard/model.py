from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def build_model(features: str = "word") -> Pipeline:
    """Return an explainable text-classification pipeline."""
    if features not in {"word", "char"}:
        raise ValueError("features must be word or char")
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    analyzer="word" if features == "word" else "char_wb",
                    ngram_range=(1, 2) if features == "word" else (3, 5),
                    min_df=1,
                    max_features=3000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            ),
        ]
    )


def most_influential_terms(model: Pipeline, count: int = 12) -> tuple[list[str], list[str]]:
    """Return terms that most strongly support each class."""
    if count < 1:
        raise ValueError("count must be positive")
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    terms = vectorizer.get_feature_names_out()
    weights = classifier.coef_[0]

    phishing_order = weights.argsort()[-count:][::-1]
    legitimate_order = weights.argsort()[:count]
    return terms[phishing_order].tolist(), terms[legitimate_order].tolist()
