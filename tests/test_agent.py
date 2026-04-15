"""
Tests for ai_agent utilities that do NOT require a live LLM:
  - JSON extraction tolerance
  - AgentResult shape
  - ScheduleReviewAgent deterministic validators (via monkeypatched _act)
"""
from datetime import date

import pytest

from ai_agent import (
    AgentResult,
    ScheduleReviewAgent,
    _extract_json,
    _validate_conflict,
)
from pawpal_system import Owner, Pet, Scheduler, Task


class TestJsonExtractor:
    def test_strict_json(self):
        assert _extract_json('{"issues": []}') == {"issues": []}

    def test_json_with_prose_wrapper(self):
        # Haiku sometimes returns: "Sure! Here is the JSON:\n\n{...}\n\nThanks!"
        raw = "Sure! Here is the JSON you requested:\n\n{\"issues\": []}\n\nDone."
        assert _extract_json(raw) == {"issues": []}

    def test_json_with_code_fence(self):
        raw = "```json\n{\"issues\": [{\"kind\": \"conflict\"}]}\n```"
        parsed = _extract_json(raw)
        assert parsed["issues"][0]["kind"] == "conflict"

    def test_no_json_raises(self):
        with pytest.raises(ValueError):
            _extract_json("I could not produce JSON, sorry.")


class TestAgentResult:
    def test_ok_true_when_no_error(self):
        r = AgentResult(text="hi", confidence=0.8)
        assert r.ok is True

    def test_ok_false_with_error(self):
        r = AgentResult(text="nope", confidence=0.0, error="bad")
        assert r.ok is False


class TestValidators:
    """
    The validators are the guardrail between the LLM and the UI — if the
    model hallucinates "conflict at 11:00", the validator must reject it.
    """

    def _owner_with_conflict(self):
        owner = Owner("T")
        a = Pet("A", "dog"); b = Pet("B", "cat")
        owner.add_pet(a); owner.add_pet(b)
        a.add_task(Task("Walk", "08:00", 20, "high", due_date=date.today()))
        b.add_task(Task("Meds", "08:00", 5,  "high", due_date=date.today()))
        return owner

    def test_conflict_validator_accepts_real_conflict(self):
        scheduler = Scheduler(self._owner_with_conflict())
        ok, _ = _validate_conflict({"target_time": "08:00"}, scheduler)
        assert ok

    def test_conflict_validator_rejects_fake_time(self):
        scheduler = Scheduler(self._owner_with_conflict())
        ok, reason = _validate_conflict({"target_time": "11:00"}, scheduler)
        assert not ok
        assert "11:00" in reason

    def test_conflict_validator_rejects_when_no_conflicts(self):
        owner = Owner("T")
        pet = Pet("Solo", "dog"); owner.add_pet(pet)
        pet.add_task(Task("Walk", "08:00", 20, "high", due_date=date.today()))
        ok, _ = _validate_conflict({"target_time": "08:00"}, Scheduler(owner))
        assert not ok


class TestAgentCheckStage:
    """
    Drive the review agent's CHECK stage directly by stubbing _act — this
    exercises the validator + confidence math without hitting the network.
    """

    def _scheduler_with_conflict(self):
        owner = Owner("T")
        a = Pet("A", "dog"); b = Pet("B", "cat")
        owner.add_pet(a); owner.add_pet(b)
        a.add_task(Task("Walk", "08:00", 20, "high", due_date=date.today()))
        b.add_task(Task("Meds", "08:00", 5,  "high", due_date=date.today()))
        return Scheduler(owner)

    def test_agent_accepts_valid_conflict_and_drops_fake(self, monkeypatch):
        scheduler = self._scheduler_with_conflict()
        agent = ScheduleReviewAgent(scheduler)

        monkeypatch.setattr(agent, "_plan", lambda: [])
        monkeypatch.setattr(agent, "_act", lambda snippets: {
            "issues": [
                {"kind": "conflict", "summary": "Walk vs Meds at 08:00",
                 "target_time": "08:00", "evidence": "[1]"},
                {"kind": "conflict", "summary": "fake conflict at 11:00",
                 "target_time": "11:00", "evidence": "[2]"},
            ]
        })
        result = agent.review()
        assert result.ok
        assert "08:00" in result.text
        assert "11:00" not in result.text       # fake conflict filtered out
        # 1 of 2 accepted -> confidence = 0.4 + 0.5 * 0.5 = 0.65
        assert 0.6 <= result.confidence <= 0.7

    def test_agent_handles_no_issues(self, monkeypatch):
        scheduler = self._scheduler_with_conflict()
        agent = ScheduleReviewAgent(scheduler)
        monkeypatch.setattr(agent, "_plan", lambda: [])
        monkeypatch.setattr(agent, "_act", lambda snippets: {"issues": []})
        result = agent.review()
        assert result.ok
        assert "No blocking issues" in result.text

    def test_agent_rejects_unknown_kind(self, monkeypatch):
        scheduler = self._scheduler_with_conflict()
        agent = ScheduleReviewAgent(scheduler)
        monkeypatch.setattr(agent, "_plan", lambda: [])
        monkeypatch.setattr(agent, "_act", lambda snippets: {
            "issues": [{"kind": "made-up-kind", "summary": "x",
                        "target_time": None, "evidence": "[1]"}]
        })
        result = agent.review()
        assert result.ok
        assert "No blocking issues" in result.text
