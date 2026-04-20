#server.py
from flask import Flask, request, jsonify, send_file
import os
import uuid
import json
from web3 import Web3
from flask_cors import CORS

from app.components.crypto_component import CryptoComponent
from app.components.s3_component import S3Component
from app.components.context_component import ContextComponent
from app.components.fl_component import FLComponent
from app.components.user_component import UserComponent
from app.components.file_component import FileComponent

app = Flask(__name__)
CORS(app)

# Configure S3
S3_BUCKET = "governance-hub-files-arshin"
S3_REGION = "ap-south-2"

# Components (now using Waters11)
crypto = CryptoComponent()
s3c = S3Component(S3_BUCKET, region_name=S3_REGION)
context_comp = ContextComponent()
fl_comp = FLComponent()
# fl_comp.client_train_and_report({
#     "location": {"chennai": 10, "mumbai": 5},
#     "device": {"laptop1": 8, "phone1": 3}
# })
user_comp = UserComponent()
file_comp = FileComponent()

# 🔥 ADD THIS BLOCK HERE (TEMP FIX)
try:
    crypto.load_master_keys()
except:
    crypto.setup(force=True)
    crypto.save_master_keys()

# print("⚡ Regenerating user key for alice (FIX)")
# new_sk = crypto.generate_user_secret(["role:prof", "dept:cs"])
# user_comp.set_user_abe_sk("alice", new_sk)

UPLOAD_TEMP_DIR = "uploads"
os.makedirs(UPLOAD_TEMP_DIR, exist_ok=True)

# --- Blockchain Configuration ---
# Use the RPC URL from your Anvil terminal
RPC_URL = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
CONTRACT_ADDRESS ="0x5FbDB2315678afecb367f032d93F642f64180aa3"
CONTRACT_ABI = [
    {
        "type": "function",
        "name": "logAccess",
        "inputs": [
            {"name": "_username", "type": "string"},
            {"name": "_fileId", "type": "string"},
            {"name": "_action", "type": "string"},
            {"name": "_granted", "type": "bool"},
            {"name": "_reason", "type": "string"}
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    }
]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
# Using the first default account from Anvil
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ACCOUNT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

def log_to_blockchain(username, file_id, action, granted, reason):
    """Sends an access audit log to the Ethereum Smart Contract and returns gas used."""
    try:
        nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        tx = contract.functions.logAccess(
            username, file_id, action, granted, reason
        ).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # --- NEW: Capture receipt to get gas metrics ---
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        gas_used = receipt.get('gasUsed', 0)
        
        print(f"Blockchain Audit Logged: {file_id} for {username} (TX: {w3.to_hex(tx_hash)}) | Gas: {gas_used}")
        return gas_used  # Returning this allows your benchmark script to save it
    except Exception as e:
        print(f"Blockchain logging failed: {e}")
        return 0
# ---------------- Register ----------------
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No input data provided"}), 400

        username = data.get("username")
        attrs = data.get("attributes", [])
        location = data.get("location", "")
        department = data.get("department", "")

        print(f"--- Processing Registration for {username} ---")

        ok, res = user_comp.register_user(username, attrs, location, department)
        if not ok:
            return jsonify({"success": False, "error": res}), 400

        # Waters11 CP-ABE Setup
        try:
            crypto.load_master_keys()
        except Exception:
            print("Master keys missing, initializing...")
            crypto.setup(force=True)
            crypto.save_master_keys()

        # Generate Key
        abe_sk_b64 = crypto.generate_user_secret(attrs)
        user_comp.set_user_abe_sk(username, abe_sk_b64)

        try:
            log_to_blockchain(username, "N/A", "REGISTER_USER", True, f"Sttrs: {','.join(attrs)}")
        except Exception as be:
            print(f"Blockchain logging failed but user was registered: {be}")
        
        return jsonify({"success": True, "message": "User registered", "user": res})

    except Exception as e:
        # This prevents the CLI JSONDecodeError by returning a JSON error instead of an HTML 500 page
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- Login (for CLI compat) ----------------
@app.route("/login", methods=["POST"])
def login():
    j = request.json
    username = j.get("username")
    user = user_comp.get_user(username)
    if not user:
        return jsonify({"ok": False, "error": "unknown user"}), 404
    return jsonify({"ok": True, "user": user}), 200

# ---------------- Upload ----------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "file missing"}), 400

        f = request.files['file']
        username = request.form.get("username") or request.form.get("owner")

        if not username:
            return jsonify({"success": False, "error": "missing username"}), 400

        policy = request.form.get("policy")
        if not policy:
            return jsonify({"success": False, "error": "policy required"}), 400

        # Context fields
        context_policy_json = request.form.get("context_policy")
        allowed_locations = request.form.get("allowed_locations")
        required_device = request.form.get("required_device")
        required_department = request.form.get("required_department")
        time_window_json = request.form.get("time_window")

        fname = f.filename
        local_path = os.path.join(UPLOAD_TEMP_DIR, f"{uuid.uuid4()}_{fname}")
        f.save(local_path)

        # 🔐 Encrypt
        try:
            crypto.load_master_keys()
            meta = crypto.encrypt_file_hybrid(local_path, policy)
        except Exception as e:
            print("Encryption error:", e)
            return jsonify({"success": False, "error": str(e)}), 500

        # ☁️ Upload to S3
        s3_key = f"enc/{uuid.uuid4()}_{fname}.enc"

        upload_ok = s3c.upload_file(meta["enc_file_path"], s3_key)

        if not upload_ok:
            return jsonify({"success": False, "error": "S3 upload failed"}), 500

        print("✅ S3 Upload success:", s3_key)

        # 📦 Register
        fid = file_comp.register_encrypted_file(username, meta, s3_key=s3_key)

        # 🔗 Blockchain
        log_to_blockchain(username, fid, "UPLOAD", True, policy)

        # 📍 Context policy
        applied_policy = None

        if context_policy_json:
            try:
                cp = json.loads(context_policy_json)
                applied_policy = cp
                context_comp.add_policy(fid, cp)
                file_comp.set_context_policy(fid, cp)
            except Exception as e:
                print("Invalid context_policy_json:", e)

        if not applied_policy:
            cp = {}

            if allowed_locations:
                cp["allowed_locations"] = [
                    x.strip().lower() for x in allowed_locations.split(",") if x.strip()
                ]

            if required_device:
                cp["allowed_devices"] = [required_device.strip().lower()]

            if required_department:
                cp["required_department"] = required_department.strip().lower()

            if time_window_json:
                try:
                    cp["time_window"] = json.loads(time_window_json)
                except Exception as e:
                    print("Invalid time_window:", e)

            if cp:
                context_comp.add_policy(fid, cp)
                file_comp.set_context_policy(fid, cp)

        # 🧹 Cleanup
        try:
            if os.path.exists(meta["enc_file_path"]):
                os.remove(meta["enc_file_path"])
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception as e:
            print("Cleanup error:", e)

        return jsonify({
            "success": True,
            "file_id": fid,
            "s3_key": s3_key
        }), 200

    except Exception as e:
        print("🔥 UPLOAD CRASH:", e)
        import traceback
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ---------------- List ----------------
@app.route("/list_files", methods=["GET"])
def list_files():
    return jsonify({"ok": True, "files": file_comp.list_files()})

# Alias for CLI
@app.route("/list", methods=["GET"])
def list_files_alias():
    return list_files()

@app.route("/files", methods=["GET"])
def get_files():
    files = file_comp.list_files()

    result = []

    for f in files:
        fid = f.get("id")   # ✅ correct key

        if not fid:
            print("⚠️ Missing ID:", f)
            continue

        result.append({
            "name": f.get("orig_filename", "unknown"),
            "owner": f.get("uploader", "unknown"),   # ✅ FIXED
            "type": f.get("orig_filename", "").split(".")[-1] if f.get("orig_filename") else "unknown",
            "file_id": fid   # ✅ FIXED
        })

    return jsonify(result), 200

# ---------------- Download ----------------

@app.route("/download", methods=["POST"])

def download():

    j = request.json

    username = j.get("username")

    fid = j.get("file_id")

    context = j.get("context") or j.get("user_context") or {}

    user = user_comp.get_user(username)

    if not user:

        return jsonify({"success": False, "error": "unknown user"}), 404

    fmeta = file_comp.get_file(fid)

    if not fmeta:

        return jsonify({"success": False, "error": "unknown file"}), 404

    # ---------------- ✅ NORMALIZATION FIX ----------------

    context["location"] = context.get("location", "").strip().lower()

    device_val = context.get("device_id", context.get("device", "")).strip().lower()
    context["device"] = device_val
    context["device_id"] = device_val

    context["department"] = context.get("department", "").strip().lower()
    context["client_id"] = username

    # remove duplicate key


    # keep existing behavior

    context["client_id"] = username

    print("✅ NORMALIZED CONTEXT:", context)

    # ---------------- Context-aware access control ----------------

    if not context_comp.check_access(fid, context):

        log_to_blockchain(username, fid, "DOWNLOAD", False, "Context Policy Denied")

        return jsonify({"success": False, "error": "context policy denied"}), 403

    # ---------------- FL anomaly check ----------------

    score = fl_comp.score_access(context)

    print("📊 FL SCORE:", score)

    # 🔧 relaxed threshold (was 0.6)

    threshold = 0.99

    if score >= threshold:

        log_to_blockchain(username, fid, "DOWNLOAD", False, f"FL Anomaly (Score: {score})")

        return jsonify({"success": False, "error": "access flagged", "score": score}), 403

    # ---------------- BACK TO S3 DOWNLOAD ----------------

    s3_key = fmeta.get("s3_key")
    if not s3_key:
        return jsonify({"success": False, "error": "file not in s3"}), 500

    local_tmp = os.path.join(UPLOAD_TEMP_DIR, f"dl_{uuid.uuid4()}.enc")
    if not s3c.download_file(s3_key, local_tmp):
        return jsonify({"success": False, "error": "s3 download failed"}), 500

    encrypted_meta = {
        "orig_filename": fmeta["orig_filename"],
        "enc_file_path": local_tmp,
        "abe_ct": fmeta["abe_ct"],
        "policy": fmeta["policy"],
    }

    abe_sk_b64 = user.get("abe_sk")
    if not abe_sk_b64:
        return jsonify({"success": False, "error": "user has no Waters11 abe key"}), 500

    try:
        crypto.load_master_keys()
        dec_path = crypto.decrypt_file_hybrid(encrypted_meta, abe_sk_b64)

        log_to_blockchain(username, fid, "DOWNLOAD", True, "Authorized and Decrypted")

        pqc_pub_key = j.get("pqc_public_key")
        if pqc_pub_key:
            with open(dec_path, 'rb') as f:
                pqc_package = crypto.pqc_encrypt_wrap(f.read(), pqc_pub_key)
            os.remove(dec_path)
            return jsonify({"success": True, "pqc_package": pqc_package})
    except Exception as e:
        return jsonify({"success": False, "error": f"Waters11 decryption failed: {e}"}), 500
    try:
        os.remove(local_tmp)
    except Exception:
        pass
    return send_file(dec_path, as_attachment=True, download_name=fmeta["orig_filename"])

# ---------------- DELETE ----------------
@app.route("/delete", methods=["POST"])
def delete_file():
    try:
        data = request.get_json()
        file_id = data.get("file_id")
        print("DELETE REQUEST:", data)
        if not file_id:
            return jsonify({"success": False, "error": "Missing file_id"}), 400

        file_meta = file_comp.get_file(file_id)
        if not file_meta:
            return jsonify({"success": False, "error": "File not found"}), 404

        # Delete from S3
        s3_key = file_meta.get("s3_key")
        if s3_key:
            s3c.delete_file(s3_key)

        # Delete from DB
        file_comp.delete_file(file_id)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#ADD THIS CRITICAL CODE TO START THE SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
