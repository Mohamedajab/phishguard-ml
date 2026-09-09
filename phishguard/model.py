from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def build_model() -> Pipeline:
    """Return an explainable text-classification pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
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
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    terms = vectorizer.get_feature_names_out()
    weights = classifier.coef_[0]

    phishing_order = weights.argsort()[-count:][::-1]
    legitimate_order = weights.argsort()[:count]
    return terms[phishing_order].tolist(), terms[legitimate_order].tolist()

