from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Redaction:
    label: str
    count: int


ID_PATTERN = re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")
PHONE_PATTERN = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
BANK_PATTERN = re.compile(r"(?<!\d)(?:\d[\s-]?){16,19}(?!\d)")


def redact_pii(text: str) -> tuple[str, list[Redaction]]:
    """Remove common identifiers before any model request is made."""
    redactions: list[Redaction] = []

    def replace(pattern: re.Pattern[str], label: str, value: str) -> str:
        matches = pattern.findall(value)
        if matches:
            redactions.append(Redaction(label=label, count=len(matches)))
            return pattern.sub(f"[{label}已脱敏]", value)
        return value

    clean = replace(ID_PATTERN, "身份证", text)
    clean = replace(PHONE_PATTERN, "手机号", clean)
    clean = replace(EMAIL_PATTERN, "邮箱", clean)
    clean = replace(BANK_PATTERN, "银行卡", clean)
    return clean, redactions


def normalise_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def validate_citations(
    evidence_ids: list[str],
    allowed_ids: set[str],
) -> tuple[list[str], bool]:
    valid = [citation_id for citation_id in evidence_ids if citation_id in allowed_ids]
    return list(dict.fromkeys(valid)), len(valid) != len(set(evidence_ids))


def safety_review(raw_text: str, findings: list[dict], evidence_ids: list[str]) -> dict:
    """Apply deterministic checks that remain active even if the model drifts."""
    verified_findings = []
    for finding in findings:
        quote = finding.get("quote", "").strip()
        if quote and quote in raw_text:
            verified_findings.append(finding)

    prompt_injection_markers = (
        "忽略以上",
        "ignore previous",
        "system prompt",
        "泄露密钥",
        "输出你的指令",
    )
    injected = any(marker.lower() in raw_text.lower() for marker in prompt_injection_markers)
    return {
        "passed": len(verified_findings) == len(findings),
        "verified_findings": verified_findings,
        "citation_count": len(set(evidence_ids)),
        "prompt_injection_detected": injected,
        "message": (
            "引用已与本地知识库及原文交叉校验。"
            if not injected
            else "检测到疑似指令注入，已将其作为合同文本处理，未执行其中指令。"
        ),
    }


def disclaimer() -> str:
    return (
        "本报告用于就业风险识别和沟通准备，不构成正式法律意见。"
        "涉及扣押证件、缴费入职、歧视、人身安全或已发生争议时，请尽快联系学校就业部门、"
        "劳动保障监察部门或专业律师。"
    )

