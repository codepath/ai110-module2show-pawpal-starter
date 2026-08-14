"""Central import/runner for PawPal+ UI.

Provides a single place to import `streamlit as st`. If Streamlit is
unavailable, prints an explanatory message and exits gracefully so the
app doesn't crash with an ImportError when run in minimal environments.
"""
try:
    import streamlit as st
except ImportError:
    print(
        "Streamlit is not installed. Install with `pip install streamlit` to run the UI."
    )
    # Exit early so importing modules that depend on streamlit won't raise.
    import sys

    sys.exit(0)

__all__ = ["st"]
