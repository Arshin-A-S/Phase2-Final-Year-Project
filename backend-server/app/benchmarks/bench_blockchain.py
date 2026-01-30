import time
import os
import sys

# Ensure the app directory is in the path
# 1. Get absolute path of benchmarks folder
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Get path to backend-server (benchmarks -> app -> backend-server)
project_root = os.path.dirname(os.path.dirname(current_dir))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.server import log_to_blockchain

def benchmark_blockchain():
    print("=== Blockchain Auditing Pillar Performance ===")
    print("[!] Ensure Anvil is running and contract is deployed.")
    
    iterations = 5
    latencies = []

    for i in range(iterations):
        start = time.time()
        # Log a simulated secure access event
        log_to_blockchain(f"bench_user_{i}", f"file_uuid_{i}", "DOWNLOAD", True, "Audit Performance Test")
        latency = (time.time() - start) * 1000
        latencies.append(latency)
        print(f"Iteration {i+1}: Logged in {latency:.2f} ms")
    
    avg_lat = sum(latencies) / iterations
    print("-" * 30)
    print(f"Average Blockchain Audit Latency: {avg_lat:.2f} ms")
    print("[*] Recommendation: Copy 'Gas used' from your Anvil Terminal for the Paper.")

if __name__ == "__main__":
    benchmark_blockchain()