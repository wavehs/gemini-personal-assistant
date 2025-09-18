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

    Args:
        user_id: The ID of the user.
        key: The key of the data to update.
        value: The new value to set.
    """
    data = _load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {}
    data[user_id_str][key] = value
    _save_data(data)
