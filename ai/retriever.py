
"""Small, deterministic retriever for attributed local pet-care notes."""

from pathlib import Path
import re

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
STOP_WORDS = set("a an and are as at be can do for from how i in is it my of on or our should the their to what when where with you your".split())


def tokenize(text: str) -> set[str]:
    """Normalize common inflections for overlap scoring without a dependency."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word[:-3] if word.endswith("ing") and len(word) > 5 else
            word[:-1] if word.endswith("s") and len(word) > 4 else word
            for word in words if word not in STOP_WORDS}


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Find relevant paragraphs in the local knowledge base."""
    if not query.strip() or top_k < 1:
        return []

    query_words = tokenize(query)
    if not query_words:
        return []
    results = []

    for path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        header, _, body = content.partition("\n\n")
        metadata = dict(line.split(": ", 1) for line in header.splitlines() if ": " in line)
        species = metadata.get("Species")
        if species and ({"dog", "cat"} & query_words) and species not in query_words:
            continue
        paragraphs = re.split(r"\n\s*\n", body)

        for index, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            overlap = query_words & tokenize(paragraph)
            score = len(overlap)

            if score > 0:
                results.append({
                    "source": path.name,
                    "title": metadata.get("Title", path.stem.replace("_", " ").title()),
                    "url": metadata.get("URL", ""),
                    "chunk_id": f"{path.stem}:{index}",
                    "text": paragraph,
                    "score": score,
                })

    results.sort(key=lambda item: (-item["score"], item["source"], item["chunk_id"]))
    return results[:top_k]
