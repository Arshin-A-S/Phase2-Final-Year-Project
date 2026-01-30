import time
import os
import sys
import json

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.server import log_to_blockchain

def benchmark_blockchain():
    print("=== Blockchain Auditing Pillar Performance ===")
    print("[!] Ensure Anvil is running and server.py returns gas used.")
    
    perf_data = {
        "layer": "Blockchain", 
        "average_latency_ms": 0, 
        "total_gas_consumed": 0,
        "average_gas_per_tx": 0,
        "runs": []
    }

    # Drastically varied scenarios to induce big gas variations for graphs
    test_scenarios = [
        {"user": "alice", "reason": "Normal"},                                     # ~11 bytes
        {"user": "user_med", "reason": "Standard_Access_Audit_Log_" * 5},          # ~130 bytes
        {"user": "user_large", "reason": "Authorized_Research_Data_Access_" * 15}, # ~450 bytes
        {"user": "auditor_xl", "reason": "Security_Context_Shield_Validation_" * 30}, # ~900 bytes
        {"user": "admin_max", "reason": "Emergency_Override_Full_Audit_Trail_Report_" * 45} # ~2000+ bytes
    ]

    latencies = []
    gas_values = []

    for i, scenario in enumerate(test_scenarios):
        # Calculate approximate bytes being sent in the string fields
        # This is what you will use for your X-axis in the graph
        payload_bytes = len(scenario["user"]) + len(scenario["reason"]) + len(f"file_id_{i}") + len("DOWNLOAD")
        
        start = time.time()
        
        # Call server.py function which now returns the gasUsed from the receipt
        gas = log_to_blockchain(
            scenario["user"], 
            f"file_id_{i}", 
            "DOWNLOAD", 
            True, 
            scenario["reason"]
        )
        
        latency = (time.time() - start) * 1000
        
        latencies.append(latency)
        gas_values.append(gas)
        
        perf_data["runs"].append({
            "scenario_index": i + 1,
            "payload_bytes": payload_bytes, # Added explicitly for your JSON
            "latency_ms": round(latency, 2),
            "gas_used": gas
        })
        
        print(f"Run {i+1}: {payload_bytes} Bytes -> Gas: {gas} | Latency: {latency:.2f} ms")
    
    # Calculate Summary Averages
    perf_data["average_latency_ms"] = round(sum(latencies) / len(test_scenarios), 2)
    perf_data["total_gas_consumed"] = sum(gas_values)
    perf_data["average_gas_per_tx"] = round(sum(gas_values) / len(test_scenarios), 2)

    # Save to file
    output_dir = os.path.join(current_dir, "results")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "blockchain_performance.json"), "w") as f:
        json.dump(perf_data, f, indent=4)
    
    print("-" * 40)
    print(f"Average Audit Latency: {perf_data['average_latency_ms']} ms")
    print(f"Average Gas Cost: {perf_data['average_gas_per_tx']}")
    print(f"[!] Variation Data saved to {output_dir}/blockchain_performance.json")

if __name__ == "__main__":
    benchmark_blockchain()