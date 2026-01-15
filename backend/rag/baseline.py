"""
This module implements a simple in-memory baseline retrieval mechanism for the
dialogue system. It stores a limited history of recent user messages to provide
basic context without relying on graph traversals or vector search.
"""

from collections import deque, defaultdict
from typing import Dict, Deque

# Configuration
_MAX_HISTORY_LENGTH = 5
# Process-local storage for user history. 
# Using deque with maxlen handles eviction automatically.
_USER_MEMORY: Dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=_MAX_HISTORY_LENGTH))

def add_user_message(user_id: str, message: str) -> None:
    """
    Stores a user message in the in-memory history.
    Retains only the last K messages defined by _MAX_HISTORY_LENGTH.

    Args:
        user_id (str): Unique identifier for the user.
        message (str): The text content of the user's message.
    """
    _USER_MEMORY[user_id].append(message)

def build_baseline_context(user_id: str) -> str:
    """
    Retrieves the stored message history for a user and formats it into
    a natural-language context string.

    Args:
        user_id (str): Unique identifier for the user.

    Returns:
        str: A formatted string summarizing previous messages, or an empty string
             if no history exists.
    """
    history = _USER_MEMORY.get(user_id)
    
    if not history:
        return ""

    lines = ["Previous conversation:"]
    for msg in history:
        lines.append(f"- {msg}")
    
    return "\n".join(lines)

