# cli.py
from client.api_client import APIClient
from client.user_client import UserClient
from client.file_client import FileClient
import os, datetime

class CLIApp:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        api = APIClient(base_url)
        self.user_cli = UserClient(api)
        self.file_cli = FileClient(api)
        self.logged_in = None

    def run(self):
        while True:
            print("\n====== MENU ======")
            print("1. Register")
            print("2. Login")
            print("3. Upload File")
            print("4. List Files")
            print("5. Download File")
            print("6. Exit")
            print("\n===================")
            choice = input("Choice: ").strip()
            if choice == "1":
                self.do_register()
            elif choice == "2":
                self.do_login()
            elif choice == "3":
                self.do_upload()
            elif choice == "4":
                self.do_list()
            elif choice == "5":
                self.do_download()
            elif choice == "6":
                break
            else:
                print("Invalid")

    def do_register(self):
        username = input("Username: ").strip()
        raw = input("Attributes (comma sep): ").strip()
        attrs = [x.strip() for x in raw.split(",") if x.strip()]
        loc = input("Primary location: ").strip()
        dept = input("Department: ").strip()
        res, code = self.user_cli.register(username, attrs, loc, dept)
        print(res)

    def do_login(self):
        username = input("Username: ").strip()
        res, code = self.user_cli.login(username)
        if code == 200 and res.get("ok"):
            self.logged_in = res["user"]
            self.logged_in["username"] = username
            print("Logged in:", self.logged_in["id"])
        else:
            print("Login failed", res)

    def do_upload(self):
        if not self.logged_in:
            print("Login first"); return
        path = input("Path to file: ").strip()
        if not os.path.exists(path):
            print("File not found"); return
        policy = input("Policy (e.g., professor AND cs): ").strip()
        allowed = input("Allowed locations (comma) leave blank: ").strip()
        allowed_list = [x.strip() for x in allowed.split(",")] if allowed else None
        req_dept = input("Required department (optional): ").strip() or None
        req_dev = input("Required device (optional): ").strip() or None
        tw = input("Add time window? y/n: ").strip().lower()
        time_window = None
        if tw == "y":
            start = input("start HH:MM: ")
            end = input("end HH:MM: ")
            tz = input("timezone (default UTC): ").strip() or "UTC"
            time_window = {"start":start,"end":end,"tz":tz}
        res, code = self.file_cli.upload_file(path, self.logged_in["id"], policy, allowed_list, req_dept, req_dev, time_window)
        print(res)

    def do_list(self):
        res, code = self.file_cli.list_files()
        if code == 200 and res.get("ok"):
            for item in res["files"]:
                # Show user-friendly information
                display_name = item.get('display_name', item.get('orig_filename', 'Unknown'))
                print(f"File: {display_name}")
                print(f"ID: {item['id']}")
                print(f"Uploaded: {item['created']}")
                print("---")
        else:
            print("Failed", res)


    def do_download(self):
        if not self.logged_in:
            print("Login first"); return
        fid = input("File ID: ").strip()
        loc = input("Your current location: ").strip()
        dev = input("Your device name: ").strip()
        dept = input("Your department: ").strip()
        hour = datetime.datetime.now().hour
        features = [hour, 0, 0]
        save_to = input("Save to filename: ").strip() or "downloaded.bin"
        
        # FIXED: Use stored username instead of user ID
        res, code = self.file_cli.download_file(self.logged_in["username"], fid, {"location":loc,"device":dev,"department":dept}, features, save_to)
        print(res)


if __name__ == "__main__":
    CLIApp().run()

