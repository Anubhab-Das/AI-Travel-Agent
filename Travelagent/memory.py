# memory.py

from typing import Dict, List

class ConversationMemory:
    def __init__(self):
        self.history: List[str] = []
        self.known_trip_data = {}

    def add_user_message(self, message: str):
        self.history.append(f"User: {message}")

    def add_assistant_message(self, message: str):
        self.history.append(f"Assistant: {message}")

    def update_trip_data(self, data: Dict[str, str]):
        self.known_trip_data.update(data)

    def get_trip_data_str(self) -> str:
        """Return a single string describing known trip data."""
        if not self.known_trip_data:
            return ""
        return " ".join(f"{k}:{v}" for k, v in self.known_trip_data.items())

    def get_full_history(self) -> str:
        return "\n".join(self.history)

# ✅ Create global memory instance here to avoid circular imports
GLOBAL_MEMORY = ConversationMemory()
