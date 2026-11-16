from __future__ import annotations

from dataclasses import dataclass
import unicodedata


class ChannelValidationError(ValueError):
    """Raised when an advice message violates the frozen channel contract."""


@dataclass(frozen=True)
class ValidatedAdvice:
    text: str
    character_count: int


def normalize_and_validate(message: str, character_cap: int) -> ValidatedAdvice:
    if character_cap < 0:
        raise ChannelValidationError("character cap must be nonnegative")
    if not isinstance(message, str):
        raise ChannelValidationError("advice must be a string")

    normalized = unicodedata.normalize("NFC", message)
    if "\n" in normalized or "\r" in normalized:
        raise ChannelValidationError("advice must be exactly one line")
    if any(unicodedata.category(ch).startswith("C") for ch in normalized):
        raise ChannelValidationError("advice contains a control or formatting character")

    count = len(normalized)
    if count > character_cap:
        raise ChannelValidationError(
            f"advice has {count} characters but cap is {character_cap}"
        )
    return ValidatedAdvice(normalized, count)


def empty_advice() -> ValidatedAdvice:
    return ValidatedAdvice("", 0)

