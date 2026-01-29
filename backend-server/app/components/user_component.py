# backend/components/user_component.py
import json
import os
import uuid
from datetime import datetime

DB_PATH = "db.json"

def load_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({"users": {}, "files": {}}, f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

class UserComponent:
    def __init__(self):
        self.db = load_db()

    def register_user(self, username, attrs, location, department): # Added department
        if username in self.db["users"]:
            return False, "User exists"
        uid = str(uuid.uuid4())
        self.db["users"][username] = {
            "id": uid,
            "attributes": attrs,
            "location": location,
            "department": department, # Added department
            "created": datetime.utcnow().isoformat(),
            "abe_sk": None,
        }
        save_db(self.db)
        return True, self.db["users"][username]

    def set_user_abe_sk(self, username, sk_b64):
        if username not in self.db["users"]:
            return False
        self.db["users"][username]["abe_sk"] = sk_b64
        save_db(self.db)
        return True

    def get_user(self, username):
        return self.db["users"].get(username)

    def list_users(self):
        return list(self.db["users"].keys())
