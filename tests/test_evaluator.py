"""
Tests that the evaluator itself behaves correctly — it's the thing we trust
to tell us whether everything else is working, so it needs a sanity net.
"""
from evaluator import run_all


class TestEvaluator:
    def test_all_canonical_checks_pass(self):
        report = run_all()
        failed = [r for r in report.results if not r.passed]
        assert not failed, "Evaluator check(s) failed: " + ", ".join(
            f"{r.name} ({r.detail})" for r in failed
        )

    def test_report_exposes_score(self):
        report = run_all()
        assert 0.0 <= report.score <= 1.0
        assert report.total > 0

    def test_markdown_render_contains_counts(self):
        report = run_all()
        md = report.as_markdown()
        assert f"{report.passed}/{report.total}" in md
