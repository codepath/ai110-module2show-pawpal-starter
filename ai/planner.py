"""Review-only AI care proposals checked by the deterministic scheduler."""

from copy import deepcopy
import json
import os
import re

from ai.gemini_client import SECRET, generate_json, input_guard, validated_citations
from ai.retriever import retrieve, tokenize
from pawpal_system import Owner, Scheduler, Task

PLAN_SCHEMA = {
    "type": "object", "required": ["summary", "citations", "tasks"],
    "properties": {
        "summary": {"type": "string"},
        "citations": {"type": "array", "items": {"type": "string"}},
        "tasks": {"type": "array", "items": {"type": "object", "required": ["pet_index", "name", "duration_minutes", "priority"],
            "properties": {"pet_index": {"type": "integer"}, "name": {"type": "string"},
                           "duration_minutes": {"type": "integer"}, "priority": {"type": "string"}}}},
    },
}


def propose_care_plan(request: str, owner: Owner, scheduler: Scheduler) -> dict:
    """Interpret, retrieve, propose, then validate without touching saved objects."""
    trace = []

    def step(name: str, detail: str):
        trace.append({"step": name, "detail": detail})

    guarded = input_guard(request)
    if guarded:
        step("Interpret request", "Stopped by input or safety guard.")
        return {"status": "guarded", "message": guarded, "trace": trace, "tasks": [], "sources": []}
    step("Interpret request", "General care-planning request accepted.")
    docs = retrieve(request, top_k=4)
    step("Retrieve knowledge", f"Found {len(docs)} matching local chunks.")
    if not docs:
        return {"status": "no_knowledge", "message": "No relevant care knowledge was found.", "trace": trace, "tasks": [], "sources": []}
    if not owner.pets:
        step("Inspect context", "No pets are configured.")
        return {"status": "no_pets", "message": "Add a pet before requesting a care plan.", "trace": trace, "tasks": [], "sources": []}
    context = [{"index": i, "name": pet.name, "species": pet.species,
                "pending_tasks": [t.name for t in pet.tasks if not t.completed]}
               for i, pet in enumerate(owner.pets)]
    step("Inspect context", f"Read {len(context)} pet(s), {len(owner.get_all_tasks())} task(s), and a {owner.available_minutes}-minute budget.")
    if not os.getenv("GEMINI_API_KEY"):
        step("Model proposal", "Skipped: Gemini API key is missing.")
        return {"status": "missing_api_key", "message": "Set GEMINI_API_KEY to request AI care proposals. Existing scheduling remains available.", "trace": trace, "tasks": [], "sources": []}
    prompt = json.dumps({
        "request": request, "pets": context, "available_minutes": owner.available_minutes,
        "knowledge": [{"id": d["chunk_id"], "text": d["text"]} for d in docs],
        "task": "Propose at most 3 new, nonmedical care tasks supported by the knowledge. Use valid pet indices, durations 1-240 minutes, priorities high/medium/low. Do not duplicate existing tasks. Give a concise summary and supporting chunk IDs. Do not assign an appointment time or say tasks were saved.",
    })
    try:
        payload = generate_json(prompt, PLAN_SCHEMA)
        sources = validated_citations(payload, docs)
        summary = payload.get("summary")
        proposals = payload.get("tasks")
        if not isinstance(summary, str) or not summary.strip() or SECRET.search(summary) or not isinstance(proposals, list) or not 1 <= len(proposals) <= 3:
            raise ValueError("invalid proposal")
        if re.search(r"\b(?:dosage|\d+\s?mg|diagnos(?:is|ed))\b", summary, re.I):
            raise ValueError("medical proposal")
        step("Model proposal", f"Received {len(proposals)} candidate task(s) with validated source IDs.")
        clone = deepcopy(owner)
        created = []
        evidence_words = set().union(*(tokenize(d["text"]) for d in sources))
        for proposal in proposals:
            if not isinstance(proposal, dict):
                raise ValueError("invalid task")
            pet_index = proposal.get("pet_index")
            name = proposal.get("name")
            duration = proposal.get("duration_minutes")
            priority = proposal.get("priority")
            if type(pet_index) is not int or not 0 <= pet_index < len(clone.pets):
                raise ValueError("invalid pet")
            if not isinstance(name, str) or len(name) > 60 or not (tokenize(name) & evidence_words):
                raise ValueError("unsupported task")
            if re.search(r"medicat|dose|prescri|diagnos|treat|poison", name, re.I):
                raise ValueError("medical task")
            if type(duration) is not int or duration > 240:
                raise ValueError("invalid duration")
            task = Task(name=name, duration_minutes=duration, priority=priority)
            pet = clone.pets[pet_index]
            if any(t.name.casefold() == task.name.casefold() and not t.completed for t in pet.tasks):
                raise ValueError("duplicate task")
            pet.add_task(task)
            created.append((pet_index, task))
        step("Validate tasks", f"Validated {len(created)} task(s) against pet identity, task fields, duplicate names, and source terms.")
        plan = scheduler.generate_plan(clone)
        selected = {id(entry["task"]) for entry in plan["selected"]}
        skipped = {id(entry["task"]): entry["reason"] for entry in plan["skipped"]}
        tasks = [{"pet": owner.pets[i].name, "name": task.name,
                  "duration_minutes": task.duration_minutes, "priority": task.priority,
                  "budget_result": "Fits today's budget" if id(task) in selected else skipped.get(id(task), "Not selected")}
                 for i, task in created]
        step("Check schedule", f"Scheduler selected {sum(id(task) in selected for _, task in created)} of {len(created)} proposals under the existing budget.")
        step("Present for review", "Suggestions only; no tasks were added or saved.")
        return {"status": "ok", "message": summary.strip() + " " + " ".join(f"[{d['chunk_id']}]" for d in sources),
                "trace": trace, "tasks": tasks, "sources": sources}
    except Exception:
        step("Validate proposal", "Model response was unavailable or failed source/task validation.")
        return {"status": "unavailable", "message": "I couldn't verify a safe care plan. Try another request or consult a veterinarian for health concerns.",
                "trace": trace, "tasks": [], "sources": []}
