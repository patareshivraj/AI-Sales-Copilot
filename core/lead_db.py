import json
import os

DB_FILE = "outputs/seen_leads.json"

class LeadDatabase:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w") as f:
                json.dump([], f)

    def get_seen_companies(self):
        try:
            with open(DB_FILE, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return set()

    def add_companies(self, companies):
        seen = self.get_seen_companies()
        seen.update(companies)
        with open(DB_FILE, "w") as f:
            json.dump(list(seen), f, indent=4)
