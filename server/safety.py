from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Redaction:
    kind: str
    count: int


PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
ID_CARD = re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")
EMAIL = re.compile(
    r"(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9.-])",
    re.IGNORECASE,
)
BANK_CARD = re.compile(r"(?<!\d)(?:\d[\s-]?){16,19}(?!\d)")


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def redact_sensitive(text: str) -> tuple[str, list[Redaction]]:
    found: list[Redaction] = []

    def replace(pattern: re.Pattern[str], label: str, value: str) -> str:
        matches = pattern.findall(value)
        if matches:
            found.append(Redaction(label, len(matches)))
            return pattern.sub(f"[{label}已脱敏]", value)
        return value

    clean = replace(ID_CARD, "证件号", text)
    clean = replace(PHONE, "手机号", clean)
    clean = replace(EMAIL, "邮箱", clean)
    clean = replace(BANK_CARD, "卡号", clean)
    return clean, found


def sanitize_chat_history(value: object, max_messages: int = 12) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value[-max_messages:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        result.append({"role": role, "content": normalise_text(content)[:3000]})
    return result


def boundary_text() -> str:
    return (
        "智能反诈训练系统提供风险识别与安全演练，不替代警方或平台官方结论。"
        "如已转账、泄露验证码或对方持续威胁，请立即停止操作，联系银行并拨打110报警。"
    )

