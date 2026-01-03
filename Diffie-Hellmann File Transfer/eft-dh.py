#!/usr/bin/env python3

import socket
import sys
import hashlib
import os
import struct
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# DH parameters
g = 2
p = int(
    "00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd"
    "551a504feb4346d2aef47053311ceaba95f6c540b967b9409e9f0502e598cfc71327c5a455e2e807"
    "bede1e0b7d23fbea054b951ca964eaecae7ba842ba1fc6818c453bf19eb9c5c86e723e69a210d4b7"
    "2561cab97b3fb3060b",
    16
)
param_numbers = dh.DHParameterNumbers(p, g)
dh_parameters = param_numbers.parameters()

def derive_key(shared_key: bytes) -> bytes:
    shared_int = int.from_bytes(shared_key, 'big')
    hex_string = '%x' % shared_int
    digest = hashlib.sha256(hex_string.encode('utf-8')).digest()
    return digest[:32]

def int_to_padded_decimal_string(value: int, length: int = 384) -> str:
    dec_str = str(value)
    return dec_str.zfill(length)

def padded_decimal_string_to_int(padded_str: str) -> int:
    return int(padded_str, 10)

def encrypt_and_send_stdin(conn, session_key):
    plaintext = sys.stdin.buffer.read()
    nonce = os.urandom(16)
    aesgcm = AESGCM(session_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    length = 16 + len(ciphertext)  
    length_bytes = struct.pack('>H', length)
    segment = length_bytes + nonce + ciphertext
    conn.sendall(segment)
    


def receive_and_decrypt_file(conn, session_key):
    length_bytes = conn.recv(2)
    if len(length_bytes) < 2:
        raise ValueError("Failed to receive length field")

    length = struct.unpack('>H', length_bytes)[0]
    data = b''
    while len(data) < length:
        chunk = conn.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Connection closed prematurely!")
        data += chunk

    if len(data) < 16:
        raise ValueError("Segment too short to contain nonce")

    nonce = data[:16]
    ciphertext = data[16:]
    aesgcm = AESGCM(session_key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")

    file_path = "decrypted_output.txt" 

    try:   
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"[Server] Could not delete existing file: {e}", file=sys.stderr)

        with open(file_path, "wb") as f:
            f.write(plaintext)
            f.flush()
            os.fsync(f.fileno())
        print(f"[Server] Wrote {len(plaintext)} bytes to {file_path}", file=sys.stderr)
        
    except Exception as e:
        print(f"[Server] Error writing to file {file_path}: {e}", file=sys.stderr)
        raise

    print("[Server] Decrypted data written to 'decrypted_output.txt'", file=sys.stderr)

def run_server(port):
    HOST = '0.0.0.0'

    private_key = dh_parameters.generate_private_key()
    public_key = private_key.public_key()
    pub_val_int = public_key.public_numbers().y
    pub_val_str = int_to_padded_decimal_string(pub_val_int)
   

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(60)
        s.bind((HOST, port))
        s.listen(1)
        print(f"[Server] Listening on port {port}...", file=sys.stderr)

        conn, addr = s.accept()
        with conn:
            print(f"[Server] Connection from {addr}", file=sys.stderr)
            conn.sendall(pub_val_str.encode('utf-8'))

            client_pub_bytes = b''
            while len(client_pub_bytes) < 384:
                chunk = conn.recv(384 - len(client_pub_bytes))
                if not chunk:
                    raise ConnectionError("Client closed connection early.")
                client_pub_bytes += chunk
            client_pub_str = client_pub_bytes.decode('utf-8')
            if len(client_pub_str) != 384:
                raise ValueError(f"Invalid client public key length: {len(client_pub_str)} (expected 384)")
            client_pub_val = padded_decimal_string_to_int(client_pub_str)

            client_public_numbers = dh.DHPublicNumbers(client_pub_val, param_numbers)
            client_public_key = client_public_numbers.public_key()
            shared_secret = private_key.exchange(client_public_key)
            session_key = derive_key(shared_secret)

            print("[Server] Waiting to receive encrypted file...", file=sys.stderr)
            receive_and_decrypt_file(conn, session_key)
            print("[Server] File received and decrypted successfully.", file=sys.stderr)


def run_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(60)
        print(f"[Client] Connecting to {host}:{port}...", file=sys.stderr)
        s.connect((host, port))

        server_pub_bytes = b''
        while len(server_pub_bytes) < 384:
            chunk = s.recv(384 - len(server_pub_bytes))
            if not chunk:
                raise ConnectionError("Server closed connection early!")
            server_pub_bytes += chunk
        server_pub_str = server_pub_bytes.decode('utf-8')
        if len(server_pub_str) != 384:
            raise ValueError(f"Invalid server public key length: {len(server_pub_str)} (expected 384)")
        server_pub_val = padded_decimal_string_to_int(server_pub_str)
        server_pub_numbers = dh.DHPublicNumbers(server_pub_val, param_numbers)
        server_public_key = server_pub_numbers.public_key()

        private_key = dh_parameters.generate_private_key()
        public_key = private_key.public_key()
        pub_val_int = public_key.public_numbers().y
        pub_val_str = int_to_padded_decimal_string(pub_val_int)
        s.sendall(pub_val_str.encode('utf-8'))

        

        shared_secret = private_key.exchange(server_public_key)
        session_key = derive_key(shared_secret)

        print("[Client] Encrypting and sending data...", file=sys.stderr)
        encrypt_and_send_stdin(s, session_key)
        print("[Client] File sent successfully.", file=sys.stderr)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DH File Transfer")
    parser.add_argument('-l', '--listen', type=int, metavar='PORT', help='Run as server listening on PORT')
    parser.add_argument('server_ip', nargs='?', help='Server IP to connect to')
    parser.add_argument('port', nargs='?', type=int, help='Port number')

    args = parser.parse_args()

    try:
        if args.listen is not None:
            run_server(args.listen)
        else:
            if args.server_ip is None or args.port is None:
                parser.print_usage(sys.stderr)
                print("\nError: Client mode requires SERVER_IP_ADDRESS and PORT.")
                sys.exit(1)
            run_client(args.server_ip, args.port)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)
