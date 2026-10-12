# Network Traffic Encryption Performance Analysis

## Cryptography / Network Security Microproject

This project experimentally compares encrypted and unencrypted network data transmission using Python. AES-256-GCM is used for encryption, while Python TCP sockets simulate network communication.

### Objectives
- Measure AES-256-GCM encryption time.
- Measure AES-256-GCM decryption time.
- Measure unencrypted and encrypted transmission time.
- Calculate total encrypted processing time.
- Calculate throughput.
- Monitor CPU and memory utilization.
- Repeat experiments and calculate average and standard deviation.
- Generate graphs comparing encrypted and unencrypted communication.

### Technology Stack
- Python 3
- AES-256-GCM
- PyCryptodome
- Python socket programming
- Pandas
- Matplotlib
- psutil
- CSV
- VS Code

### Project Structure

```text
Network_Traffic_Encryption_Performance_Analysis/
├── main.py
├── analyze_results.py
├── requirements.txt
├── README.md
├── results/
│   └── results.csv
└── graphs/
    ├── transmission_time.png
    ├── encryption_decryption_time.png
    ├── total_time.png
    ├── throughput.png
    └── cpu_memory.png
```

### Installation

```bash
python -m pip install -r requirements.txt
```

### Run the experiment

```bash
python main.py
```

The program tests several data sizes and repeats each test multiple times. Results are saved to:

```text
results/results.csv
```

### Generate graphs

```bash
python analyze_results.py
```

Graphs are saved in:

```text
graphs/
```

### Experimental Notes

The network experiment uses `127.0.0.1` (localhost), so the measurements represent communication between processes on the same computer. This removes Internet/Wi-Fi variability and makes the encryption overhead easier to observe.

The encrypted test uses AES-256-GCM. GCM provides confidentiality and authentication. The authentication tag and nonce are included in the transmitted encrypted packet.

Actual results depend on the computer, operating system, Python version, background processes, and hardware. Do not replace measured results with invented values.

### Main Metrics

- Encryption Time (ms)
- Decryption Time (ms)
- Unencrypted Transmission Time (ms)
- Encrypted Transmission Time (ms)
- Encrypted Total Time (ms)
- Unencrypted Throughput (Mbps)
- Encrypted Throughput (Mbps)
- CPU Usage (%)
- Memory Usage (%)

### Suggested Viva Explanation

The experiment compares a plaintext TCP transmission with an AES-256-GCM protected TCP transmission. For each data size, multiple trials are performed. Encryption and decryption processing times are measured separately, while socket transfer time is measured independently. The results are stored in CSV format and analyzed with Pandas. Matplotlib is then used to visualize the security-performance trade-off.

## Wireshark Demonstration

Use `wireshark_demo.py` for the live security demonstration.

1. Open Wireshark.
2. Select **Adapter for loopback traffic capture**.
3. Start capturing.
4. Apply this display filter:

```text
tcp.port == 5055 && tcp.len > 0
```

5. In a separate Command Prompt, run:

```bash
python wireshark_demo.py
```

The program sends the same recognizable message twice:
- First as plaintext.
- Then encrypted with AES-256-GCM.

The plaintext TCP payload can be inspected in Wireshark, while the AES-GCM payload appears as ciphertext. The demo uses a fixed key only for this local classroom demonstration; it is not intended as production key management.

For the actual performance experiment, continue to use:

```bash
python main.py
python analyze_results.py
```

## Streamlit UI

The project also includes `app.py`, a graphical dashboard for running the experiment and demonstrating the Wireshark traffic.

Start the UI with:

```bash
streamlit run app.py
```

The dashboard includes:
- Data-size and trial controls.
- AES-256-GCM performance measurements.
- Encryption/decryption/transmission/total time.
- Throughput comparison.
- CPU and memory measurements.
- CSV download.
- A dedicated Wireshark demonstration that sends plaintext and AES-GCM traffic.

## HTML/CSS/JavaScript UI

A standalone professional cybersecurity dashboard is included in:

\\	ext
frontend/
|-- index.html   <- open this in any browser
|-- style.css
|-- script.js
|-- README.md
\
### Quick Start

\\ash
# Step 1 - install Python dependencies
pip install -r requirements.txt

# Step 2 - run the experiment (generates results/results.csv)
python main.py

# Step 3 - (optional) generate PNG graphs
python analyze_results.py

# Step 4 - open the dashboard
start frontend/index.html       # Windows
open  frontend/index.html       # macOS
xdg-open frontend/index.html    # Linux
\
Or serve locally:

\\ash
cd frontend
python -m http.server 8080
# then open http://localhost:8080
\
### Dashboard Pages

| Page | What it shows |
|---|---|
| **Dashboard** | 9 metric cards, 5 Canvas charts, 5 Matplotlib PNGs. All loaded from real CSV. |
| **Live Experiment** | Step-by-step terminal workflow. Explains browser limitation clearly. |
| **Results & History** | Sortable, searchable table (17 columns). Row detail panel. CSV export. |
| **Wireshark Demo** | Loads wireshark_demo_results.json. Shows actual message, ciphertext hex, packet sizes. |
| **About Project** | Methodology, formulas, architecture diagram, limitations, technology stack. |

### Loading Results

1. Run \python main.py\ to generate esults/results.csv\.
2. Open \rontend/index.html\.
3. Click **Load results.csv** and select the file.

For the Wireshark Demo:
1. Run \python wireshark_demo.py\.
2. Navigate to **Wireshark Demo** in the sidebar.
3. Click **Load wireshark_demo_results.json**.

### Port usage

Both \main.py\ and \wireshark_demo.py\ use TCP port **5055**. Do not run them simultaneously.

### Data integrity

- The UI never shows hardcoded or invented performance numbers.
- All metric cards show -- until a real CSV is loaded.
- Charts render only actual measured values from \main.py\.
- The Wireshark page clearly states wireshark_demo_results.json is demonstration metadata, not a PCAP capture file.

## Final Data Flow

\main.py --> results/results.csv --> frontend dashboard
analyze_results.py --> graphs/ --> Dashboard PNG section
wireshark_demo.py --> TCP on 127.0.0.1:5055 (capture in Wireshark)
wireshark_demo.py --> wireshark_demo_results.json --> Wireshark Demo page
\
The UI intentionally does not display fabricated performance numbers.
