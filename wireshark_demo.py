import json
import socket
import threading
import time
from pathlib import Path

from Crypto.Cipher import AES


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "127.0.0.1"
PORT = 5055

MESSAGE = (
    b"CONFIDENTIAL MESSAGE | "
    b"Network Traffic Encryption | "
    b"AES-256-GCM Demonstration"
)

# 32 bytes = 256-bit AES key
DEMO_KEY = b"0123456789ABCDEF0123456789ABCDEF"

# Result file used by the HTML/CSS/JS UI
WIRESHARK_RESULT_FILE = (
    Path(__file__).resolve().parent
    / "results"
    / "wireshark_demo_results.json"
)


# ============================================================
# TCP HELPER FUNCTIONS
# ============================================================

def receive_exactly(sock, size):
    """Receive exactly 'size' bytes from a TCP socket."""
    data = bytearray()

    while len(data) < size:
        chunk = sock.recv(min(4096, size - len(data)))

        if not chunk:
            raise ConnectionError(
                "Connection closed before all data was received."
            )

        data.extend(chunk)

    return bytes(data)


def receive_with_length(sock):
    """Receive a length-prefixed message."""
    length = int.from_bytes(
        receive_exactly(sock, 8),
        "big"
    )

    return receive_exactly(sock, length)


def send_with_length(sock, data):
    """Send data preceded by an 8-byte length."""
    sock.sendall(len(data).to_bytes(8, "big"))
    sock.sendall(data)


# ============================================================
# TCP SERVER
# ============================================================

def server(expected_connections=2):
    """
    TCP server that receives:
    1. Plaintext message
    2. AES-256-GCM encrypted message
    """

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server_socket:

        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        print(f"[SERVER] Listening on {HOST}:{PORT}")

        for _ in range(expected_connections):

            connection, address = server_socket.accept()

            with connection:

                payload = receive_with_length(connection)

                print(
                    f"[SERVER] Received {len(payload)} bytes "
                    f"from {address[0]}:{address[1]}"
                )

                connection.sendall(b"ACK")


# ============================================================
# SEND DATA
# ============================================================

def transmit(payload):
    """
    Connect to the TCP server and transmit the payload.
    Returns transmission time in seconds.
    """

    with socket.create_connection(
        (HOST, PORT),
        timeout=10
    ) as client:

        start_time = time.perf_counter()

        send_with_length(
            client,
            payload
        )

        acknowledgement = receive_exactly(
            client,
            3
        )

        end_time = time.perf_counter()

    if acknowledgement != b"ACK":
        raise RuntimeError(
            "Invalid server acknowledgement."
        )

    return end_time - start_time


# ============================================================
# AES-256-GCM ENCRYPTION
# ============================================================

from Crypto.Random import get_random_bytes

def encrypt_message(message):
    """
    Encrypt message using AES-256-GCM.

    Packet format:

    [nonce length]
    [nonce]
    [tag length]
    [authentication tag]
    [ciphertext]
    """

    nonce = get_random_bytes(12)

    cipher = AES.new(
        DEMO_KEY,
        AES.MODE_GCM,
        nonce=nonce
    )

    ciphertext, tag = cipher.encrypt_and_digest(
        message
    )

    encrypted_packet = (
        len(nonce).to_bytes(1, "big")
        + nonce
        + len(tag).to_bytes(1, "big")
        + tag
        + ciphertext
    )

    return encrypted_packet, nonce, tag, ciphertext


# ============================================================
# MAIN DEMONSTRATION
# ============================================================

def main():

    print("=" * 70)
    print("WIRESHARK PLAINTEXT vs AES-256-GCM DEMONSTRATION")
    print("=" * 70)

    print()
    print("Wireshark filter:")
    print("    tcp.port == 5055 && tcp.len > 0")
    print()

    # --------------------------------------------------------
    # START SERVER
    # --------------------------------------------------------

    server_thread = threading.Thread(
        target=server,
        args=(2,),
        daemon=True
    )

    server_thread.start()

    # Give server time to start
    time.sleep(0.5)

    # --------------------------------------------------------
    # DEMO 1 — PLAINTEXT
    # --------------------------------------------------------

    print("[1] PLAINTEXT TRANSMISSION")
    print("-" * 70)

    print(MESSAGE.decode())

    print()
    print(
        ">>> Capture this packet in Wireshark."
    )

    print(
        ">>> The readable message should be visible "
        "in the packet bytes."
    )

    print()

    plaintext_time = transmit(
        MESSAGE
    )

    print(
        f"[CLIENT] Plaintext transmission time: "
        f"{plaintext_time * 1000:.3f} ms"
    )

    # --------------------------------------------------------
    # WAIT BEFORE ENCRYPTED TRANSMISSION
    # --------------------------------------------------------

    time.sleep(3)

    # --------------------------------------------------------
    # DEMO 2 — AES-256-GCM
    # --------------------------------------------------------

    encrypted_packet, nonce, tag, ciphertext = encrypt_message(
        MESSAGE
    )

    plaintext_size = len(MESSAGE)
    encrypted_payload_size = len(encrypted_packet)
    payload_overhead = encrypted_payload_size - plaintext_size

    nonce_size = len(nonce)
    tag_size = len(tag)
    metadata_size = 2

    tcp_framing_size = 8
    framed_application_size = tcp_framing_size + encrypted_payload_size

    assert encrypted_payload_size == plaintext_size + nonce_size + tag_size + metadata_size, "Encrypted payload size mismatch!"

    print()
    print("[2] AES-256-GCM ENCRYPTED TRANSMISSION")
    print("-" * 70)

    print(
        f"Original message size : "
        f"{plaintext_size} bytes"
    )

    print(
        f"Encrypted packet size : "
        f"{encrypted_payload_size} bytes"
    )

    print()

    print(
        ">>> Capture this packet in Wireshark."
    )

    print(
        ">>> The original message should NOT be "
        "readable in the payload."
    )

    print()

    encrypted_time = transmit(
        encrypted_packet
    )

    print(
        f"[CLIENT] Encrypted transmission time: "
        f"{encrypted_time * 1000:.3f} ms"
    )

    # --------------------------------------------------------
    # SAVE RESULT FOR HTML/CSS/JS UI
    # --------------------------------------------------------

    WIRESHARK_RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload_overhead_percent = (
        payload_overhead / plaintext_size * 100
        if plaintext_size else 0
    )

    result = {
        "generated_by": "wireshark_demo.py",
        "host": HOST,
        "port": PORT,
        "wireshark_filter": (
            "tcp.port == 5055 && tcp.len > 0"
        ),

        "message": MESSAGE.decode(),

        "plaintext_size_bytes": plaintext_size,
        "encrypted_packet_size_bytes": encrypted_payload_size,
        "nonce_size_bytes": nonce_size,
        "authentication_tag_size_bytes": tag_size,
        "metadata_size_bytes": metadata_size,
        "payload_overhead_bytes": payload_overhead,
        "payload_overhead_percent": payload_overhead_percent,
        "tcp_framing_size_bytes": tcp_framing_size,
        "framed_application_size_bytes": framed_application_size,

        "plaintext_transmission_ms": round(
            plaintext_time * 1000,
            3
        ),

        "encrypted_transmission_ms": round(
            encrypted_time * 1000,
            3
        ),

        "ciphertext_hex": encrypted_packet.hex(
            " "
        ),

        "completed": True
    }

    with WIRESHARK_RESULT_FILE.open(
        "w",
        encoding="utf-8"
    ) as result_file:

        json.dump(
            result,
            result_file,
            indent=4
        )

    # --------------------------------------------------------
    # WAIT FOR SERVER
    # --------------------------------------------------------

    server_thread.join(
        timeout=2
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print()
    print(
        f"Demo results saved to:\n"
        f"{WIRESHARK_RESULT_FILE}"
    )

    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

    print()
    print(
        "In Wireshark, compare the two TCP payloads:"
    )

    print(
        "1. Plaintext  -> readable application data"
    )

    print(
        "2. AES-GCM    -> ciphertext / unreadable payload"
    )

    print()
    print(
        "Result file:"
    )

    print(
        "results/wireshark_demo_results.json"
    )

    print()
    print(
        "Note: The fixed AES key is used only for "
        "this classroom demonstration."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()