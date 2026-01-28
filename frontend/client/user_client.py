# client/user_client.py
from .api_client import APIClient

class UserClient:
    def __init__(self, api: APIClient):
        self.api = api

    def register(self, username, attributes, location="", department=""):
        payload = {"username": username, "attributes": attributes, "location": location, "department": department}
        r = self.api.post("/register", json=payload)
        return r.json(), r.status_code

    def login(self, username):
        r = self.api.post("/login", json={"username": username})
        return r.json(), r.status_code
