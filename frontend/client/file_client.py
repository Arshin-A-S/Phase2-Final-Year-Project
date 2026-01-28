# client/file_client.py
from .api_client import APIClient

class FileClient:
    def __init__(self, api: APIClient):
        self.api = api

    def upload_file(self, filepath, owner, policy, allowed_locations=None, required_department=None, required_device=None, time_window=None):
        files = {"file": open(filepath, "rb")}
        data = {"owner": owner, "policy": policy}
        if allowed_locations: data["allowed_locations"] = ",".join(allowed_locations)
        if required_department: data["required_department"] = required_department
        if required_device: data["required_device"] = required_device
        if time_window:
            import json
            data["time_window"] = json.dumps(time_window)
        r = self.api.post("/upload", files=files, data=data)
        return r.json(), r.status_code

    def list_files(self):
        r = self.api.get("/list")
        return r.json(), r.status_code

    def download_file(self, username, file_id, user_context, access_features, save_to):
        payload = {"username": username, "file_id": file_id, "user_context": user_context, "access_features": access_features}
        r = self.api.post("/download", json=payload, stream=True)
        if r.status_code == 200:
            with open(save_to, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return {"ok":True, "msg":"saved"}, 200
        try:
            return r.json(), r.status_code
        except:
            return {"ok":False, "msg":"unknown error"}, r.status_code
