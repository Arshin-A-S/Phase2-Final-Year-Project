import time
import os
import sys
import json

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.components.crypto_component import CryptoComponent
from app.components.s3_component import S3Component

def run_integration_benchmark():
    print("=== AWS S3 Integration & Latency Bottleneck Test ===")
    
    # Initialize components
    crypto = CryptoComponent()
    crypto.load_master_keys()
    
    # FIX 1: Provide your actual S3 bucket name here
    BUCKET_NAME = "file-storage-00414" 
    s3 = S3Component(bucket_name=BUCKET_NAME)
    
    file_sizes_mb = [1, 10, 50]
    test_file_path = "integration_test_temp.dat"
    results = []

    for size in file_sizes_mb:
        print(f"\n[+] Processing {size}MB Payload...")
        
        with open(test_file_path, "wb") as f:
            f.write(os.urandom(size * 1024 * 1024))

        # 1. Local Security Latency (M5 Processing)
        start_sec = time.time()
        meta = crypto.encrypt_file_hybrid(test_file_path, "role:admin")
        security_latency = (time.time() - start_sec) * 1000

        # 2. Cloud Network Latency (S3 Upload)
        enc_file_path = meta["enc_file_path"]
        s3_key = f"perf_test_{size}mb.enc"
        
        start_cloud = time.time()
        # FIX 2: S3Component.upload_file expects a local path, not raw data
        success = s3.upload_file(enc_file_path, s3_key)
        network_latency = (time.time() - start_cloud) * 1000

        if not success:
            print(f"    [!] S3 Upload Failed for {size}MB")
            continue

        total_latency = security_latency + network_latency
        results.append({
            "size_mb": size,
            "security_overhead_ms": round(security_latency, 2),
            "network_latency_ms": round(network_latency, 2),
            "total_ms": round(total_latency, 2),
            "security_share_pct": round((security_latency / total_latency) * 100, 2)
        })

        print(f"    - M5 Security: {security_latency:.2f} ms")
        print(f"    - S3 Network:  {network_latency:.2f} ms")
        print(f"    - Sec Share:   {results[-1]['security_share_pct']}%")
        
        # Cleanup local encrypted file
        if os.path.exists(enc_file_path):
            os.remove(enc_file_path)

    # Save to JSON
    out_dir = os.path.join(current_dir, "results")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "s3_integration_results.json"), "w") as f:
        json.dump(results, f, indent=4)
    
    if os.path.exists(test_file_path): os.remove(test_file_path)
    print(f"\n[!] Results saved to {out_dir}/s3_integration_results.json")

if __name__ == "__main__":
    run_integration_benchmark()