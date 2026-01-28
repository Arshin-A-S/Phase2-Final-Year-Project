# client/api_client.py
import requests

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base = base_url.rstrip("/")

    def post(self, path, json=None, files=None, data=None, stream=False):
        url = f"{self.base}{path}"
        return requests.post(url, json=json, files=files, data=data, stream=stream)

    def get(self, path, params=None):
        url = f"{self.base}{path}"
        return requests.get(url, params=params)
