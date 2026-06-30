from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MoodResult:
    label: str
    emoji: str
    confidence: float
    caregiver_note: str


NEGATIVE_TERMS = [
    "δεν νιώθω καλά",
    "πονάω",
    "κουράστηκα",
    "στεναχωρη",
    "φοβάμαι",
    "ζαλίζομαι",
    "άγχος",
    "sad",
    "pain",
    "tired",
    "dizzy",
]
POSITIVE_TERMS = ["καλά", "ωραία", "εντάξει", "χαρούμε", "ok", "good", "fine", "done", "yes"]


def detect_mood(text: str) -> MoodResult:
    normalized = text.lower().strip()
    if any(term in normalized for term in NEGATIVE_TERMS):
        return MoodResult(
            label="Needs attention",
            emoji="😟",
            confidence=0.86,
            caregiver_note="The patient may need emotional or physical support.",
        )
    if any(term in normalized for term in POSITIVE_TERMS):
        return MoodResult(
            label="Stable",
            emoji="🙂",
            confidence=0.74,
            caregiver_note="The patient appears stable in this interaction.",
        )
    return MoodResult(
        label="Neutral",
        emoji="😊",
        confidence=0.55,
        caregiver_note="No strong emotional signal detected.",
    )
