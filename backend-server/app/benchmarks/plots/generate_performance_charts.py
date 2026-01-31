import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Path Setup
RESULTS_DIR = "../results"
OUTPUT_DIR = "performance_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global style for academic paper
plt.style.use('seaborn-v0_8-paper')
sns.set_context("paper", font_scale=1.5)
sns.set_style("whitegrid")

def generate_blockchain_plots():
    print("[+] Generating Blockchain Charts...")
    with open(os.path.join(RESULTS_DIR, "blockchain_performance.json"), "r") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data['runs'])
    
    # Plot 1: Gas Consumption vs Payload Size
    plt.figure(figsize=(10, 6))
    
    # Customizing markers for maximum visibility
    sns.lineplot(
        data=df, 
        x='payload_bytes', 
        y='gas_used', 
        marker='o',          # Circular marker
        markersize=12,       # Increased size for visibility
        markerfacecolor='red',# Contrasting color for the marker interior
        markeredgecolor='black', # Adding an edge for better definition
        linewidth=2.5, 
        color='#2c3e50'
    )
    
    plt.title('Blockchain Audit Overhead: Gas vs Metadata Size')
    plt.xlabel('Payload Metadata (Bytes)')
    plt.ylabel('Gas Consumption')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "blockchain_gas_vs_size.png"), dpi=300)
    plt.close()
    
   
def generate_crypto_plots():
    print("[+] Generating Cryptography Charts...")
    with open(os.path.join(RESULTS_DIR, "crypto_performance.json"), "r") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data['file_latencies'])
    
    # Plot 3: Hybrid ABE Encryption/Decryption Scalability
    plt.figure(figsize=(10, 6))
    plt.plot(df['size_mb'], df['abe_enc_ms'], label='ABE + AES Encryption', marker='s', linewidth=2)
    plt.plot(df['size_mb'], df['abe_dec_ms'], label='ABE + AES Decryption', marker='^', linewidth=2)
    plt.title('Hybrid Cryptographic Latency vs File Size')
    plt.xlabel('File Size (MB)')
    plt.ylabel('Latency (ms)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "crypto_scalability.png"), dpi=300)
    plt.close()

    # Plot 4: Layered Overhead Comparison (Stacking)
    # Showing that PQC and ABE KeyGen are constant-time overheads
    plt.figure(figsize=(10, 6))
    labels = ['KeyGen', 'PQC Wrapping', '100MB File Proc']
    values = [data['abe_keygen_ms'], df.iloc[-1]['pqc_wrap_ms'], df.iloc[-1]['abe_dec_ms']]
    
    sns.barplot(x=labels, y=values, palette='magma')
    plt.yscale('log') # Log scale to show large differences clearly
    plt.title('System Component Latency Comparison (Log Scale)')
    plt.ylabel('Latency (ms)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "crypto_component_comparison.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_blockchain_plots()
    generate_crypto_plots()
    print(f"\n[!] All charts saved to: {os.path.abspath(OUTPUT_DIR)}")