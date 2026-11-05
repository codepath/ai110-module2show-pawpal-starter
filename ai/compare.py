"""Optional live baseline/RAG comparison; writes evidence only after real calls."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path

from google import genai
from google.genai import types

from ai.gemini_client import MODEL, SECRET, ask_gemini
from ai.planner import propose_care_plan
from pawpal_system import Owner, Pet, Scheduler

QUESTION = "How should I plan dog exercise and fresh water on a warm day?"
PLAN_REQUEST = "Suggest a short dog exercise and water routine for Mochi on a warm day."


def main() -> int:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("Live comparison skipped: GEMINI_API_KEY is absent.")
        return 2
    client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=12000))
    try:
        response = client.models.generate_content(
            model=MODEL, contents=QUESTION,
            config=types.GenerateContentConfig(max_output_tokens=200, temperature=0),
        )
        baseline = (response.text or "").strip()
    except Exception:
        print("Live comparison could not complete the no-retrieval call.")
        return 1
    finally:
        client.close()
    grounded = ask_gemini(QUESTION)
    owner = Owner("Demo", available_minutes=30, pets=[Pet("Mochi", "dog")])
    plan = propose_care_plan(PLAN_REQUEST, owner, Scheduler())
    if not baseline or grounded["status"] != "ok":
        print(f"Live comparison incomplete: grounded status={grounded['status']}; planning status={plan['status']}.")
        return 1
    record = {
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "model": MODEL, "question": QUESTION,
        "baseline": {"method": "same model, direct question, no local retrieval or specialization",
                     "answer": SECRET.sub("[redacted]", baseline), "local_citations": []},
        "rag": {"method": "local retrieval and specialized structured answer",
                "answer": grounded["answer"],
                "sources": [{"id": d["chunk_id"], "url": d["url"]} for d in grounded["sources"]]},
        "plan_request": PLAN_REQUEST,
        "plan": {"status": plan["status"], "message": plan["message"],
                 "tasks": plan["tasks"], "trace": plan["trace"]},
        "note": "Live outputs are observations, not a clinical accuracy rating or grade prediction.",
    }
    destination = Path(__file__).resolve().parents[1] / "docs" / "ai_live_comparison.json"
    destination.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded real baseline, RAG, and planning calls in {destination.relative_to(destination.parents[1])}; planning status={plan['status']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
