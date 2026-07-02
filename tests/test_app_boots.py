"""End-to-end smoke check: the Streamlit app must boot without raising.

Runs the real app via Streamlit's AppTest (no mocks) so the CI `test` job
exercises actual behavior from the very first pipeline run.
"""

from streamlit.testing.v1 import AppTest


def test_app_boots_without_exception():
    app = AppTest.from_file("app.py").run()
    assert not app.exception
