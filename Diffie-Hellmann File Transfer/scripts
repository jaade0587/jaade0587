**Encrypted File Transfer & Diffie-Hellman MITM Lab**

This repository contains a set of Python scripts demonstrating encrypted file transfer, Diffie–Hellman key exchange, and a man-in-the-middle (MITM) attack against unauthenticated DH.
The project is intended for educational and security research purposes.

**Contents**

eft.py – Password-based encrypted file transfer (baseline implementation)

eft-dh.py – Diffie–Hellman–based encrypted file transfer

dh-proxy.py – MITM proxy that intercepts and decrypts DH-encrypted traffic

1. eft.py — Encrypted File Transfer (Password-Based)

A simple encrypted file transfer tool that uses a pre-shared password to derive a symmetric key and securely transmit data over a TCP connection.

**Features**

AES-GCM encryption for confidentiality and integrity

PBKDF2 key derivation from a user-supplied password

Client/server architecture

Encrypted data sent via standard input (stdin)

**Usage**

**Server**

python3 eft.py -k password123 -l 9000


**Client**

cat file.txt | python3 eft.py -k password123 127.0.0.1 9000

**Output**

Decrypted data is written to decrypted_output.txt

Plaintext is also echoed to stdout

2. eft-dh.py — Diffie-Hellman Encrypted File Transfer

An enhanced version of encrypted file transfer that replaces the shared password with a Diffie–Hellman key exchange, establishing a session key dynamically.

**Features**

Diffie–Hellman key exchange with fixed parameters

AES-GCM encryption using derived session keys

No pre-shared secret required

Demonstrates secure key agreement over an insecure channel

**How It Works**

Client and server exchange DH public values

Both sides derive the same shared secret

A session key is derived from the shared secret

Data is encrypted and transferred securely

**Usage**

**Server**

python3 eft-dh.py -l 9000


**Client**

cat file.txt | python3 eft-dh.py 127.0.0.1 9000

**Output**

Decrypted file written to decrypted_output.txt

3. dh-proxy.py — Diffie-Hellman MITM Proxy

A man-in-the-middle proxy that exploits the lack of authentication in Diffie–Hellman key exchange.
The proxy transparently intercepts, decrypts, modifies, and re-encrypts traffic between the client and server.

**Purpose**

This script demonstrates why unauthenticated Diffie–Hellman is vulnerable to MITM attacks, even when strong encryption (AES-GCM) is used.

**Features**

Acts as a fake server to the client and a fake client to the server

Establishes two separate DH sessions

Decrypts traffic from both sides

Logs intercepted plaintext to disk

Optionally modifies data in transit

**Usage**
python3 dh-proxy.py -l 8000 REAL_SERVER_IP 9000


Then point the eft-dh.py client at the proxy instead of the real server.

**Output Files**

intercepted_by_proxy.txt — data intercepted from the client

intercepted_from_server.txt — data intercepted from the server

**Security Notes**

These tools do not authenticate peers

Diffie–Hellman without authentication is vulnerable to MITM

This project is intended for learning, testing, and demonstration only

Do not use this code in production environments

**Educational Value**

This project demonstrates:

Secure file transfer fundamentals

Key derivation and symmetric encryption

Diffie–Hellman key exchange mechanics

Practical MITM attacks on cryptographic protocols

Why authentication is critical in secure communications
