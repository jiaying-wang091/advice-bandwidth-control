from __future__ import annotations


def response_curve_not_available() -> str:
    """The Day 1-2 smoke pilot is too small for a scientific figure."""
    return "No response curve is produced before the frozen full experiment."


if __name__ == "__main__":
    print(response_curve_not_available())

