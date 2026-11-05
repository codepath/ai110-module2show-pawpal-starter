
from ai.retriever import retrieve


def test_retrieve_relevant_information():
    results = retrieve("dog exercise and fresh water")

    assert len(results) > 0
    assert results[0]["source"] == "dog_care.txt"
    assert "exercise" in results[0]["text"].lower()


def test_retrieve_empty_query():
    assert retrieve("") == []


def test_retrieve_no_matching_information():
    assert retrieve("quantum spaceship") == []


def test_retrieve_respects_top_k():
    results = retrieve("dog exercise and fresh water", top_k=2)

    assert len(results) <= 2


def test_retrieve_includes_source_and_score():
    results = retrieve("fresh water")

    assert results
    assert "source" in results[0]
    assert "chunk_id" in results[0]
    assert "score" in results[0]
