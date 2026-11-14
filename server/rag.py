from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path


CATEGORY_TERMS = {
    "probation": "试用期 工资 合同期限 转正",
    "working_time": "工作时间 加班 休息日 法定假日 加班费",
    "social_insurance": "社会保险 社保 五险一金 用工之日",
    "non_compete": "竞业限制 补偿 保密 两年",
    "penalty": "违约金 培训 招聘损失",
    "resignation": "离职 提前通知 三十日 试用期",
    "change": "调岗 工作地点 协商一致 变更",
    "validity": "无效 排除权利 法定责任",
    "contract": "书面劳动合同 必备条款 工作内容 劳动报酬",
    "action": "签约前 核对 沟通 升级 维权",
}


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    latin = re.findall(r"[a-z0-9_]{2,}", lowered)
    chinese_blocks = re.findall(r"[\u4e00-\u9fff]+", text)
    tokens = list(latin)
    for block in chinese_blocks:
        tokens.extend(block[index : index + 2] for index in range(max(1, len(block) - 1)))
        tokens.extend(block[index : index + 3] for index in range(max(1, len(block) - 2)))
    return tokens


class KnowledgeBase:
    def __init__(self, path: Path):
        self.documents = json.loads(path.read_text(encoding="utf-8"))
        self.by_id = {document["id"]: document for document in self.documents}
        self.term_frequencies = [Counter(tokenize(document["text"] + document["title"])) for document in self.documents]
        document_frequency = Counter()
        for frequencies in self.term_frequencies:
            document_frequency.update(frequencies.keys())
        total = len(self.documents)
        self.idf = {
            token: math.log((total + 1) / (frequency + 1)) + 1
            for token, frequency in document_frequency.items()
        }

    def search(self, query: str, categories: list[str], limit: int = 8) -> list[dict]:
        query_terms = Counter(tokenize(query + " " + " ".join(CATEGORY_TERMS.get(item, "") for item in categories)))
        category_set = set(categories)
        ranked: list[tuple[float, dict]] = []
        for document, frequencies in zip(self.documents, self.term_frequencies):
            lexical = sum(
                min(count, frequencies.get(term, 0)) * self.idf.get(term, 1)
                for term, count in query_terms.items()
            )
            category_bonus = 3.5 if document["category"] in category_set else 0
            action_bonus = 1.25 if document["category"] == "action" else 0
            score = lexical + category_bonus + action_bonus
            if score > 0:
                ranked.append((score, document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                **document,
                "score": round(score, 3),
            }
            for score, document in ranked[:limit]
        ]

    def get(self, evidence_id: str) -> dict | None:
        return self.by_id.get(evidence_id)

