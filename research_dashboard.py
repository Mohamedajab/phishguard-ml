import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="PhishGuard evaluation", layout="wide")
st.title("PhishGuard evaluation")
root = Path(__file__).resolve().parent / "results/research"
if not (root / "research.json").exists():
    st.info("Run python research.py first.")
    st.stop()
summary = json.loads((root / "research.json").read_text("utf-8"))
st.warning(summary["note"])
st.caption(f"Training-selected representation: {summary['selected_by_training_cv']}")
st.dataframe(pd.json_normalize(summary["models"]))
curves = pd.read_csv(root / "curves.csv")
for kind, x, y in [("ROC", "False-positive rate", "True-positive rate"), ("PR", "Recall", "Precision")]:
    st.subheader(f"{kind}: {x} versus {y}")
    import altair as alt
    chart = alt.Chart(curves[curves.curve == kind].reset_index()).mark_line().encode(
        x=alt.X("x:Q", title=x), y=alt.Y("y:Q", title=y), color="features:N", order="index:Q")
    st.altair_chart(chart, use_container_width=True)
st.subheader("Training-only threshold analysis")
thresholds = pd.read_csv(root / "thresholds.csv")
features = st.selectbox("Representation", ["word", "char"])
st.line_chart(thresholds[thresholds.features == features].set_index("threshold")[["precision", "recall", "f1"]])
st.subheader("Challenge errors")
predictions = pd.read_csv(root / "predictions.csv")
st.dataframe(predictions[(predictions.features == features) & (predictions.error != "correct")], hide_index=True)
st.caption("Probabilities are not calibrated. Curves describe only 20 synthetic messages, not deployment performance.")
