from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RESULT_FILE = BASE_DIR / "results" / "results.csv"
GRAPH_DIR = BASE_DIR / "graphs"


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(GRAPH_DIR / filename, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    GRAPH_DIR.mkdir(exist_ok=True)

    if not RESULT_FILE.exists():
        raise FileNotFoundError(
            "results/results.csv not found. Run main.py first."
        )

    df = pd.read_csv(RESULT_FILE)

    x = df["Data Size (KB)"]

    # 1. Transmission time
    plt.figure(figsize=(9, 5))
    plt.plot(
        x,
        df["Unencrypted Transmission Mean (ms)"],
        marker="o",
        label="Unencrypted"
    )
    plt.plot(
        x,
        df["Encrypted Transmission Mean (ms)"],
        marker="o",
        label="Encrypted"
    )
    plt.xlabel("Data Size (KB)")
    plt.ylabel("Transmission Time (ms)")
    plt.title("Encrypted vs Unencrypted Transmission Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_plot("transmission_time.png")

    # 2. Encryption and decryption time
    plt.figure(figsize=(9, 5))
    plt.plot(
        x,
        df["Encrypted Encryption Mean (ms)"],
        marker="o",
        label="Encryption"
    )
    plt.plot(
        x,
        df["Encrypted Decryption Mean (ms)"],
        marker="o",
        label="Decryption"
    )
    plt.xlabel("Data Size (KB)")
    plt.ylabel("Processing Time (ms)")
    plt.title("AES-256-GCM Encryption and Decryption Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_plot("encryption_decryption_time.png")

    # 3. Total time
    plt.figure(figsize=(9, 5))
    plt.plot(
        x,
        df["Unencrypted Transmission Mean (ms)"],
        marker="o",
        label="Unencrypted Total"
    )
    plt.plot(
        x,
        df["Encrypted Total Mean (ms)"],
        marker="o",
        label="Encrypted Total"
    )
    plt.xlabel("Data Size (KB)")
    plt.ylabel("Total Time (ms)")
    plt.title("Total Processing and Transmission Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_plot("total_time.png")

    # 4. Throughput
    plt.figure(figsize=(9, 5))
    plt.plot(
        x,
        df["Unencrypted Throughput (Mbps)"],
        marker="o",
        label="Unencrypted"
    )
    plt.plot(
        x,
        df["Encrypted Throughput (Mbps)"],
        marker="o",
        label="Encrypted"
    )
    plt.xlabel("Data Size (KB)")
    plt.ylabel("Throughput (Mbps)")
    plt.title("Encrypted vs Unencrypted Throughput")
    plt.legend()
    plt.grid(True, alpha=0.3)
    save_plot("throughput.png")

    # 5. CPU and memory
    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.plot(
        x,
        df["CPU Usage Mean (%)"],
        marker="o",
        label="CPU Usage (%)"
    )
    ax1.set_xlabel("Data Size (KB)")
    ax1.set_ylabel("CPU Usage (%)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(
        x,
        df["Memory Usage Mean (%)"],
        marker="s",
        label="Memory Usage (%)"
    )
    ax2.set_ylabel("Memory Usage (%)")

    plt.title("System Resource Utilization")
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / "cpu_memory.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("Analysis complete.")
    print(f"Graphs saved to: {GRAPH_DIR}")


if __name__ == "__main__":
    main()
