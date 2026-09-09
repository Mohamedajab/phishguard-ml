from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

from phishguard.data import load_messages
from phishguard.evaluation import calculate_metrics
from phishguard.model import build_model, most_influential_terms


st.set_page_config(page_title="PhishGuard", page_icon="PG", layout="wide")


@st.cache_resource
def train_demo_model():
    messages = load_messages(Path("data/messages.csv"))
    train, test = train_test_split(
        messages, test_size=0.25, random_state=42, stratify=messages["label"]
    )
    model = build_model()
    model.fit(train["text"], train["label"])
    predictions = model.predict(test["text"])
    metrics = calculate_metrics(test["label"].tolist(), predictions.tolist())
    return model, metrics, test


model, metrics, test_messages = train_demo_model()
st.title("PhishGuard")
st.caption("An explainable phishing-email classifier built for learning and reproducible evaluation")
st.warning("The model uses synthetic demonstration data and must not be treated as an email security product.")

metric_columns = st.columns(4)
for column, label, key in zip(
    metric_columns,
    ["Accuracy", "Precision", "Recall", "F1"],
    ["accuracy", "precision", "recall", "f1"],
):
    column.metric(label, f"{metrics[key]:.1%}")

st.subheader("Try a message")
subject = st.text_input("Subject", "Urgent: verify your account")
body = st.text_area(
    "Body",
    "Your account will be suspended. Confirm your password immediately through this link.",
    height=130,
)

if st.button("Classify message", type="primary"):
    probability = float(model.predict_proba([f"{subject} {body}"])[0, 1])
    label = "Likely phishing" if probability >= 0.5 else "Likely legitimate"
    st.metric(label, f"{probability:.1%} phishing probability")

phishing_terms, legitimate_terms = most_influential_terms(model, count=10)
left, right = st.columns(2)
left.subheader("Terms associated with phishing")
left.write(", ".join(phishing_terms))
right.subheader("Terms associated with legitimate mail")
right.write(", ".join(legitimate_terms))

with st.expander("Held-out examples"):
    st.dataframe(
        test_messages[["message_id", "subject", "label"]].rename(
            columns={"label": "actual_label"}
        ),
        use_container_width=True,
        hide_index=True,
    )

