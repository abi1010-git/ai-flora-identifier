from __future__ import annotations

REQUIRED_DISCLAIMER = "AI identification may be incorrect."
LOW_CONFIDENCE_MESSAGE = "Unable to confidently identify."
CONSUMPTION_WARNING = (
    "Do not eat or touch unknown plants, mushrooms, seeds, fruits, or fungi based "
    "only on an AI result. Consult a qualified local expert for high-stakes decisions."
)

FORBIDDEN_SAFETY_PHRASES = (
    "definitely safe",
    "guaranteed safe",
    "safe to eat",
    "non-toxic",
    "nontoxic",
    "guaranteed non-toxic",
)


def confidence_status(confidence: float, threshold: float) -> str:
    return "identified" if confidence >= threshold else "low_confidence"


def low_confidence_message(confidence: float, threshold: float) -> str | None:
    if confidence < threshold:
        return LOW_CONFIDENCE_MESSAGE
    return None


def contains_forbidden_safety_claim(text: str) -> bool:
    normalized = text.lower()
    return any(phrase in normalized for phrase in FORBIDDEN_SAFETY_PHRASES)

