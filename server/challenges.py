from __future__ import annotations

import json
from pathlib import Path


class ChallengeEngine:
    def __init__(self, root: Path):
        self.questions = json.loads((root / "data" / "challenges.json").read_text(encoding="utf-8"))
        self.by_id = {item["id"]: item for item in self.questions}

    def public_questions(self) -> list[dict]:
        return [
            {
                key: value
                for key, value in item.items()
                if key not in {"answer", "explanation"}
            }
            for item in self.questions
        ]

    def grade(self, answers: object) -> dict:
        if not isinstance(answers, dict):
            raise ValueError("答案格式不正确")
        details = []
        correct_count = 0
        for question in self.questions:
            selected = answers.get(question["id"])
            try:
                selected_int = int(selected)
            except (TypeError, ValueError):
                selected_int = -1
            correct = selected_int == question["answer"]
            if correct:
                correct_count += 1
            details.append(
                {
                    "id": question["id"],
                    "category": question["category"],
                    "correct": correct,
                    "selected": selected_int,
                    "answer": question["answer"],
                    "explanation": question["explanation"],
                }
            )
        total = len(self.questions)
        score = round(correct_count / total * 100)
        if score >= 90:
            level = "反诈先锋"
        elif score >= 70:
            level = "警觉达人"
        elif score >= 50:
            level = "基础过关"
        else:
            level = "需要复习"
        return {
            "score": score,
            "correct": correct_count,
            "total": total,
            "level": level,
            "details": details,
        }

