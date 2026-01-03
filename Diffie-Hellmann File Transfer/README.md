**Encrypted File Transfer & Diffie-Hellman Security Lab**

This repository contains a set of Python scripts that explore file transfer over TCP, progressing from plaintext transmission to encrypted communication, and concluding with a man-in-the-middle (MITM) attack against unauthenticated Diffie–Hellman key exchange.

The project is designed for educational and security research purposes, demonstrating both secure protocol construction and common cryptographic pitfalls.

**Project Overview**

The repository intentionally follows a progression:

Plaintext file transfer (no security)

Password-based encryption

Diffie–Hellman key exchange

Active MITM attack

This structure highlights why cryptography is necessary, how it is applied, and what goes wrong when authentication is missing.

**Contents**

uft.py
Unencrypted file transfer (baseline implementation)

eft.py
Password-based encrypted file transfer using symmetric cryptography

eft-dh.py
Diffie–Hellman–based encrypted file transfer with dynamic session keys

dh-proxy.py
Man-in-the-middle proxy exploiting unauthenticated Diffie–Hellman

**1. uft.py — Unencrypted File Transfer (Baseline)**

A minimal TCP file transfer utility with no encryption, integrity protection, or authentication.
This script serves as the baseline against which the encrypted implementations can be compared.

**Purpose**

To demonstrate how raw file transfer works over the network and why transmitting data in plaintext is insecure.

**Features**

Plain TCP socket communication

Length-prefixed framing

Client/server architecture

Streams data via stdin/stdout

No cryptographic protections

**Usage**

**Server**

python3 uft.py -l 9000 > received_file


**Client**

cat file.txt | python3 uft.py 127.0.0.1 9000

**Security Implications**

Data is transmitted in plaintext

Traffic can be read or modified by any observer on the network

Included strictly for educational comparison

**2. eft.py — Encrypted File Transfer (Password-Based)**

An encrypted file transfer tool that uses a pre-shared password to derive a symmetric encryption key.

**Features**

AES-GCM encryption (confidentiality + integrity)

PBKDF2 key derivation from a shared password

Client/server architecture

Data streamed via stdin

**How It Works**

Client derives a key from a password and random salt

File data is encrypted using AES-GCM

Encrypted payload is transmitted to the server

Server derives the same key and decrypts the data

**Usage**

**Server**

python3 eft.py -k password123 -l 9000


**Client**

cat file.txt | python3 eft.py -k password123 127.0.0.1 9000

**Output**

Decrypted file written to decrypted_output.txt

Plaintext echoed to stdout

**3. eft-dh.py — Diffie-Hellman Encrypted File Transfer**

An encrypted file transfer implementation that replaces pre-shared passwords with a Diffie–Hellman key exchange, allowing both parties to establish a shared session key dynamically.

**Features**

Diffie–Hellman key exchange with fixed parameters

AES-GCM encryption using derived session keys

No pre-shared secret required

Length-prefixed encrypted data framing

**How It Works**

Client and server exchange DH public values

A shared secret is computed independently on both sides

A session key is derived from the shared secret

File data is encrypted and transmitted securely

**Usage**

**Server**

python3 eft-dh.py -l 9000


**Client**

cat file.txt | python3 eft-dh.py 127.0.0.1 9000

**Output**

Decrypted file written to decrypted_output.txt

**4. dh-proxy.py — Diffie-Hellman MITM Proxy**

A man-in-the-middle proxy that exploits the lack of authentication in Diffie–Hellman key exchange.
The proxy transparently intercepts, decrypts, optionally modifies, and re-encrypts traffic between the client and server.

**Purpose**

To demonstrate that encryption alone is insufficient if key exchange is not authenticated.

**Features**

Acts as a fake server to the client and a fake client to the server

Establishes two independent DH sessions

Decrypts traffic from both directions

Logs intercepted plaintext to disk

Optionally modifies data in transit

**Usage**
python3 dh-proxy.py -l 8000 REAL_SERVER_IP 9000


Then configure the eft-dh.py client to connect to the proxy instead of the real server.

**Output Files**

intercepted_by_proxy.txt — data intercepted from the client

intercepted_from_server.txt — data intercepted from the server

**Security Lessons Demonstrated**

Plaintext protocols expose all data to attackers

Encryption without integrity is insufficient

Diffie–Hellman provides secure key agreement only if authenticated

AES-GCM provides confidentiality and integrity, but not peer authentication

MITM attacks are practical against unauthenticated protocols

**Educational Value**

This repository demonstrates:

Network protocol design fundamentals

Symmetric encryption and key derivation

Diffie–Hellman key exchange mechanics

Man-in-the-middle attacks in practice

The importance of authentication in secure communications

**Disclaimer**

These tools are intended for educational and research purposes only.
They are not hardened, audited, or suitable for production use.
