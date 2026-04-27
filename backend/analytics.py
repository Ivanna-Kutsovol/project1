from typing import Dict

from storage import get_analytics_from_db, increment_analytics


def increment_total() -> None:
    increment_analytics("total_messages")


def increment_topic(topic: str) -> None:
    increment_analytics(topic)


def get_analytics() -> Dict[str, int]:
    return get_analytics_from_db()
