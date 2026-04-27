from typing import List

from storage import add_message_to_db, get_history_from_db


def get_history(session_id: str) -> List[dict[str, str]]:
    return get_history_from_db(session_id)


def add_message(session_id: str, role: str, text: str) -> None:
    add_message_to_db(session_id, role, text)
