# backend/components/context_component.py
import time

class ContextComponent:
    """
    Very lightweight context-aware engine.
    You can expand rules to include time windows, geo-IP, device fingerprint, etc.
    """
    def __init__(self):
        # sample context policies store (in real system use policy language)
        self.policies = {}

    def add_policy(self, file_id, policy):
        # policy: dict with possible keys like allowed_locations, allowed_times, allowed_devices
        self.policies[file_id] = policy

    def check_access(self, file_id, context):
        pol = self.policies.get(file_id)
        if not pol:
            return True

        location = (context.get("location") or "").strip().lower()
        device = (context.get("device_id") or "").strip().lower()
        department = (context.get("department") or "").strip().lower()

        if "allowed_locations" in pol:
            allowed_locations = [x.strip().lower() for x in pol["allowed_locations"]]
            if location not in allowed_locations:
                print("❌ Location failed")
                return False

        if "allowed_devices" in pol:
            allowed_devices = [x.strip().lower() for x in pol["allowed_devices"]]
            if device not in allowed_devices:
                print("❌ Device failed")
                return False

        if "required_department" in pol:
            if department != pol["required_department"].strip().lower():
                print("❌ Department failed")
                return False

        print("✅ Context access granted")
        return True