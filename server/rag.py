from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


def tokens(text: str) -> list[str]:
    latin = re.findall(r"[a-z0-9_]{2,}", text.lower())
    chinese = re.findall(r"[\u4e00-\u9fff]+", text)
    result = list(latin)
    for block in chinese:
        result.extend(block[i : i + 2] for i in range(max(1, len(block) - 1)))
        result.extend(block[i : i + 3] for i in range(max(1, len(block) - 2)))
    return result


class FraudKnowledge:
    def __init__(self, root: Path):
        self.documents = json.loads((root / "data" / "fraud_knowledge.json").read_text(encoding="utf-8"))
        self.cases = json.loads((root / "data" / "news_cases.json").read_text(encoding="utf-8"))
        self.doc_by_id = {item["id"]: item for item in self.documents}
        self.case_by_id = {item["id"]: item for item in self.cases}
        corpus = [item["title"] + item["text"] + " ".join(item["keywords"]) for item in self.documents]
        self.tf = [Counter(tokens(text)) for text in corpus]
        frequency: Counter = Counter()
        for item in self.tf:
            frequency.update(item.keys())
        total = len(self.documents)
        self.idf = {
            token: math.log((total + 1) / (count + 1)) + 1
            for token, count in frequency.items()
        }

    def search(self, query: str, category: str | None = None, limit: int = 5) -> list[dict]:
        query_terms = Counter(tokens(query))
        ranked = []
        for document, frequencies in zip(self.documents, self.tf):
            lexical = sum(
                min(count, frequencies.get(term, 0)) * self.idf.get(term, 1)
                for term, count in query_terms.items()
            )
            category_bonus = 7 if category and document["category"] == category else 0
            keyword_bonus = sum(2 for keyword in document["keywords"] if keyword in query)
            score = lexical + category_bonus + keyword_bonus
            if score:
                ranked.append((score, document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [{**document, "score": round(score, 3)} for score, document in ranked[:limit]]

    def related_cases(self, query: str, category: str | None = None, limit: int = 3) -> list[dict]:
        ranked = []
        for case in self.cases:
            category_bonus = 8 if category and case["category"] == category else 0
            keyword_hits = sum(
                2 for tag in case["tags"] if tag in query
            )
            title_hits = sum(1 for tag in case["tags"] if tag in case["title"])
            if category_bonus or keyword_hits:
                ranked.append((category_bonus + keyword_hits + title_hits * 0.2, case))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [case for _, case in ranked[:limit]] or self.cases[:2]

    def get_document(self, evidence_id: str) -> dict | None:
        return self.doc_by_id.get(evidence_id)

