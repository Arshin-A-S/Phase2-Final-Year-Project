import time
import os
import sys

# Ensure the app directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the path to 'backend-server' (move up TWO levels)
# benchmarks/ -> app/ -> backend-server/
project_root = os.path.dirname(os.path.dirname(current_dir))

# 3. Add 'backend-server' to sys.path so 'app' is seen as a package
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 4. Use the absolute import path starting from the 'app' package
from app.components.crypto_component import CryptoComponent

def benchmark_crypto():
    crypto = CryptoComponent()
    print("=== Cryptographic Pillar Performance ===")
    
    # 1. ABE Key Generation overhead
    attrs = ["PROF", "CS", "FINAL_YEAR"]
    start = time.time()
    crypto.setup(force=True)
    crypto.save_master_keys()
    crypto.generate_user_secret(attrs)
    print(f"[+] Waters11 User Secret Key Gen (3 attributes): {(time.time() - start)*1000:.2f} ms")

    # 2. Hybrid Encryption/Decryption by File Size
    sizes = [1, 5, 10] # MB
    for size in sizes:
        test_file = f"bench_{size}mb.bin"
        with open(test_file, "wb") as f:
            f.write(os.urandom(size * 1024 * 1024))
        
        # Measure Encryption
        t0 = time.time()
        meta = crypto.encrypt_file_hybrid(test_file, "PROF AND CS")
        t_enc = (time.time() - t0) * 1000
        
        # Measure Decryption
        sk_b64 = crypto.generate_user_secret(["PROF", "CS"])
        t1 = time.time()
        crypto.decrypt_file_hybrid(meta, sk_b64)
        t_dec = (time.time() - t1) * 1000
        
        print(f"[*] File Size: {size}MB | Enc: {t_enc:.2f}ms | Dec: {t_dec:.2f}ms")
        
        # Cleanup
        if os.path.exists(test_file): os.remove(test_file)
        if os.path.exists(meta["enc_file_path"]): os.remove(meta["enc_file_path"])

    # 3. Lattice-based PQC overhead
    data = b"SymmetricKeyMaterial_AES256"
    pub, _ = crypto.pqc_keygen()
    t_pqc = time.time()
    crypto.pqc_encrypt_wrap(data, pub)
    print(f"[+] Lattice-PQC Key Wrapping Latency: {(time.time() - t_pqc)*1000:.2f} ms")

if __name__ == "__main__":
    benchmark_crypto()