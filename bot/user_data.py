import json
import os
from typing import Dict, Any

DATA_FILE = "user_data.json"

def _load_data() -> Dict[str, Any]:
    """Loads user data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_data(data: Dict[str, Any]) -> None:
    """Saves user data to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving user data: {e}")

def get_user_data(user_id: int, key: str) -> Any:
    """
    Retrieves a specific piece of data for a given user.

    Args:
        user_id: The ID of the user.
        key: The key of the data to retrieve.

    Returns:
        The value associated with the key, or None if not found.
    """
    data = _load_data()
    return data.get(str(user_id), {}).get(key)

def update_user_data(user_id: int, key: str, value: Any) -> None:
    """
    Updates or adds a specific piece of data for a given user.
    """
    data = _load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {}
    data[user_id_str][key] = value
    _save_data(data)


# --- Conversation History Functions ---

MAX_HISTORY_LENGTH = 10 # Store last 5 turns (user + model)

def get_user_history(user_id: int) -> list:
    """
    Retrieves the conversation history for a given user.
    """
    return get_user_data(user_id, 'history') or []

def add_to_user_history(user_id: int, user_message: str, model_message: str):
    """
    Adds a user message and a model response to the user's history,
    and keeps the history trimmed to a maximum length.
    """
    history = get_user_history(user_id)

    # Add the new messages in the format expected by Gemini
    history.append({"role": "user", "parts": [user_message]})
    history.append({"role": "model", "parts": [model_message]})

    # Keep the history list trimmed to the last MAX_HISTORY_LENGTH messages
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]

    update_user_data(user_id, 'history', history)

def get_all_user_ids() -> list[int]:
    """
    Returns a list of all user IDs that have data stored.
    """
    data = _load_data()
    return [int(user_id) for user_id in data.keys()]
