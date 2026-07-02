"""End-to-end check of the CLI demo: run main.py as a real subprocess."""

import subprocess
import sys

import pytest


def run_demo() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "main.py"], capture_output=True, text=True, timeout=60
    )


@pytest.fixture(scope="module")
def demo_output() -> str:
    return run_demo().stdout


def test_demo_exits_cleanly():
    assert run_demo().returncode == 0


def test_demo_prints_todays_schedule(demo_output):
    assert "Today's Schedule" in demo_output


def test_demo_prints_mochi(demo_output):
    assert "Mochi" in demo_output


def test_demo_prints_whiskers(demo_output):
    assert "Whiskers" in demo_output
