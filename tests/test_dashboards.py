from streamlit.testing.v1 import AppTest


def test_research_dashboard():
    app = AppTest.from_file("../research_dashboard.py").run(timeout=30)
    assert not app.exception
