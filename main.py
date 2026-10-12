import csv
import os
import socket
import statistics
import threading
import time
from pathlib import Path

import psutil
from Crypto.Cipher import AES


HOST = "127.0.0.1"
PORT = 5055

DATA_SIZES = [
    1 * 1024,          # 1 KB
    10 * 1024,         # 10 KB
    100 * 1024,        # 100 KB
    1 * 1024 * 1024,   # 1 MB
    5 * 1024 * 1024,   # 5 MB
]

TRIALS = 5

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULT_FILE = RESULTS_DIR / "results.csv"

AES_KEY = os.urandom(32)  # 256-bit AES key


def send_with_length(sock, data: bytes) -> None:
    """Send an 8-byte length prefix followed by the payload."""
    sock.sendall(len(data).to_bytes(8, "big"))
    sock.sendall(data)


def receive_exactly(sock, size: int) -> bytes:
    """Receive exactly size bytes from a TCP socket."""
    chunks = bytearray()

    while len(chunks) < size:
        chunk = sock.recv(min(64 * 1024, size - len(chunks)))
        if not chunk:
            raise ConnectionError("Connection closed before all data arrived.")
        chunks.extend(chunk)

    return bytes(chunks)


def receive_with_length(sock) -> bytes:
    """Receive an 8-byte length prefix and then the payload."""
    length = int.from_bytes(receive_exactly(sock, 8), "big")
    return receive_exactly(sock, length)


def encrypt_data(data: bytes):
    """Encrypt data using AES-256-GCM."""
    cipher = AES.new(AES_KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # GCM nonce is normally 16 bytes with PyCryptodome's default.
    # Store lengths explicitly so the packet format is unambiguous.
    packet = (
        len(cipher.nonce).to_bytes(1, "big")
        + cipher.nonce
        + len(tag).to_bytes(1, "big")
        + tag
        + ciphertext
    )

    return packet


def decrypt_data(packet: bytes) -> bytes:
    """Decrypt and authenticate an AES-256-GCM packet."""
    position = 0

    nonce_len = packet[position]
    position += 1
    nonce = packet[position:position + nonce_len]
    position += nonce_len

    tag_len = packet[position]
    position += 1
    tag = packet[position:position + tag_len]
    position += tag_len

    ciphertext = packet[position:]

    cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


class LocalTCPServer:
    """Small localhost TCP server used only for controlled experiments."""

    def __init__(self):
        self.stop_event = threading.Event()
        self.ready_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()
        if not self.ready_event.wait(timeout=5):
            raise RuntimeError("TCP test server failed to start.")

    def stop(self):
        self.stop_event.set()

        # Wake accept() by making a short connection.
        try:
            with socket.create_connection((HOST, PORT), timeout=0.5):
                pass
        except OSError:
            pass

        self.thread.join(timeout=2)

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((HOST, PORT))
            server_sock.listen(5)
            server_sock.settimeout(0.5)

            self.ready_event.set()

            while not self.stop_event.is_set():
                try:
                    connection, _ = server_sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break

                with connection:
                    try:
                        payload = receive_with_length(connection)

                        # The server intentionally does not perform application-level
                        # encryption/decryption. It receives the bytes and acknowledges
                        # them, allowing the client to measure socket transfer time.
                        if payload != b"__STOP__":
                            connection.sendall(b"ACK")
                    except (ConnectionError, OSError):
                        pass


def transmit(payload: bytes) -> float:
    """Transmit one payload and return socket transfer time in seconds."""
    with socket.create_connection((HOST, PORT), timeout=10) as client:
        start = time.perf_counter()
        send_with_length(client, payload)
        acknowledgement = receive_exactly(client, 3)
        end = time.perf_counter()

    if acknowledgement != b"ACK":
        raise RuntimeError("Unexpected server acknowledgement.")

    return end - start


def run_unencrypted(data: bytes):
    """Measure plaintext transmission."""
    transmission_time = transmit(data)
    return {
        "transmission_time": transmission_time,
        "total_time": transmission_time,
    }


def run_encrypted(data: bytes):
    """Measure AES encryption, transmission, and decryption separately."""
    encryption_start = time.perf_counter()
    encrypted_packet = encrypt_data(data)
    encryption_time = time.perf_counter() - encryption_start

    transmission_time = transmit(encrypted_packet)

    decryption_start = time.perf_counter()
    decrypted = decrypt_data(encrypted_packet)
    decryption_time = time.perf_counter() - decryption_start

    if decrypted != data:
        raise ValueError("Integrity check failed: decrypted data differs from input.")

    total_time = encryption_time + transmission_time + decryption_time

    return {
        "encryption_time": encryption_time,
        "transmission_time": transmission_time,
        "decryption_time": decryption_time,
        "total_time": total_time,
        "encrypted_packet_size": len(encrypted_packet),
    }


def cpu_memory_snapshot():
    """Return current CPU and memory percentages."""
    cpu = psutil.cpu_percent(interval=0.05)
    memory = psutil.virtual_memory().percent
    return cpu, memory


def mean_ms(values):
    return statistics.mean(values) * 1000


def stdev_ms(values):
    return statistics.stdev(values) * 1000 if len(values) > 1 else 0.0


def mean_mbps(size_bytes, times):
    average_seconds = statistics.mean(times)
    return (size_bytes * 8 / average_seconds) / 1_000_000


def initialize_results():
    RESULTS_DIR.mkdir(exist_ok=True)

    with RESULT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Data Size (Bytes)",
            "Data Size (KB)",
            "Trials",
            "Unencrypted Transmission Mean (ms)",
            "Unencrypted Transmission StdDev (ms)",
            "Encrypted Encryption Mean (ms)",
            "Encrypted Encryption StdDev (ms)",
            "Encrypted Transmission Mean (ms)",
            "Encrypted Transmission StdDev (ms)",
            "Encrypted Decryption Mean (ms)",
            "Encrypted Decryption StdDev (ms)",
            "Encrypted Total Mean (ms)",
            "Encrypted Total StdDev (ms)",
            "Unencrypted Throughput (Mbps)",
            "Encrypted Throughput (Mbps)",
            "CPU Usage Mean (%)",
            "Memory Usage Mean (%)",
        ])


def run_experiment():
    print("=" * 78)
    print("NETWORK TRAFFIC ENCRYPTION PERFORMANCE ANALYSIS")
    print("=" * 78)
    print(f"Host       : {HOST}")
    print(f"Port       : {PORT}")
    print(f"Algorithm  : AES-256-GCM")
    print(f"Trials     : {TRIALS}")
    print()

    initialize_results()
    server = LocalTCPServer()
    server.start()

    try:
        for size in DATA_SIZES:
            print("-" * 78)
            print(f"DATA SIZE: {size / 1024:.2f} KB")
            print("-" * 78)

            data = os.urandom(size)

            plain_times = []
            enc_times = []
            enc_transmission_times = []
            dec_times = []
            total_times = []
            cpu_values = []
            memory_values = []

            for trial in range(1, TRIALS + 1):
                cpu, memory = cpu_memory_snapshot()

                plain_result = run_unencrypted(data)
                encrypted_result = run_encrypted(data)

                plain_times.append(plain_result["transmission_time"])
                enc_times.append(encrypted_result["encryption_time"])
                enc_transmission_times.append(
                    encrypted_result["transmission_time"]
                )
                dec_times.append(encrypted_result["decryption_time"])
                total_times.append(encrypted_result["total_time"])
                cpu_values.append(cpu)
                memory_values.append(memory)

                print(
                    f"Trial {trial}/{TRIALS} | "
                    f"Plain: {plain_result['transmission_time'] * 1000:.3f} ms | "
                    f"Encrypt: {encrypted_result['encryption_time'] * 1000:.3f} ms | "
                    f"Encrypted Tx: {encrypted_result['transmission_time'] * 1000:.3f} ms | "
                    f"Decrypt: {encrypted_result['decryption_time'] * 1000:.3f} ms"
                )

            row = [
                size,
                size / 1024,
                TRIALS,
                mean_ms(plain_times),
                stdev_ms(plain_times),
                mean_ms(enc_times),
                stdev_ms(enc_times),
                mean_ms(enc_transmission_times),
                stdev_ms(enc_transmission_times),
                mean_ms(dec_times),
                stdev_ms(dec_times),
                mean_ms(total_times),
                stdev_ms(total_times),
                mean_mbps(size, plain_times),
                mean_mbps(size, total_times),
                statistics.mean(cpu_values),
                statistics.mean(memory_values),
            ]

            with RESULT_FILE.open("a", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(row)

            print()
            print(f"Average plaintext transmission : {row[3]:.3f} ms")
            print(f"Average encryption time         : {row[5]:.3f} ms")
            print(f"Average encrypted transmission : {row[7]:.3f} ms")
            print(f"Average decryption time         : {row[9]:.3f} ms")
            print(f"Average encrypted total        : {row[11]:.3f} ms")
            print(f"Plaintext throughput            : {row[13]:.2f} Mbps")
            print(f"Encrypted throughput            : {row[14]:.2f} Mbps")
            print()

    finally:
        server.stop()

    print("=" * 78)
    print("EXPERIMENT COMPLETED")
    print(f"Results saved to: {RESULT_FILE}")
    print("=" * 78)


if __name__ == "__main__":
    run_experiment()
