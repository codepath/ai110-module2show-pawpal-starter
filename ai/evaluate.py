"""Run the deterministic AI evaluation subset with pytest reporting."""

from pathlib import Path
import pytest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    return pytest.main([str(root / "tests" / "test_ai_evaluation.py"), "-q", "-p", "no:cacheprovider"])


if __name__ == "__main__":
    raise SystemExit(main())
