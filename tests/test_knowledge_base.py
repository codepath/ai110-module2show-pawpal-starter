"""
Tests for the RAG retriever + knowledge base. No network required.
"""
import pytest

from knowledge_base import corpus_size, format_context, retrieve


class TestCorpus:
    def test_corpus_has_enough_entries(self):
        # A real RAG should have a non-trivial corpus — guard against accidental
        # deletions.
        assert corpus_size() >= 10


class TestRetriever:
    @pytest.mark.parametrize("query,expected_topic", [
        ("how long should I walk my dog every morning", "dog-exercise"),
        ("my cat needs playtime indoors",               "cat-enrichment"),
        ("give medicine at the same time",              "medication-timing"),
        ("brushing a long-haired dog",                  "grooming-cadence"),
        ("puppy potty training",                        "puppy-schedule"),
    ])
    def test_canonical_query_finds_right_topic(self, query, expected_topic):
        hits = retrieve(query, k=3)
        topics = [h.topic for h in hits]
        assert expected_topic in topics, f"{query!r} -> {topics}"

    def test_respects_k(self):
        hits = retrieve("dog walk feeding play", k=2)
        assert len(hits) <= 2

    def test_irrelevant_query_returns_nothing(self):
        # min_score guard: off-topic queries must NOT be grounded on random
        # snippets. If this fails, confidence in the RAG layer is broken.
        assert retrieve("xyzzy foobar nonsense gibberish", k=3) == []

    def test_ordering_is_deterministic(self):
        a = retrieve("morning walk dog energy", k=3)
        b = retrieve("morning walk dog energy", k=3)
        assert [s.topic for s in a] == [s.topic for s in b]


class TestFormatContext:
    def test_empty_context_is_safe(self):
        assert "no relevant guidance" in format_context([])

    def test_context_includes_numbered_citations(self):
        hits = retrieve("dog exercise", k=2)
        text = format_context(hits)
        assert "[1]" in text
        if len(hits) > 1:
            assert "[2]" in text
