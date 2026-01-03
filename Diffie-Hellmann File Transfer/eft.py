#!/usr/bin/env python3



import argparse

import sys

import socket

from Crypto.Protocol.KDF import PBKDF2

from Crypto.Util.Padding import pad, unpad

from Crypto.Hash import SHA256

from Crypto.Cipher import AES

from Crypto.Random import get_random_bytes

from struct import pack, unpack



def parse_args():

    parser = argparse.ArgumentParser(description="Encrypted File Transfer (EFT)")

    parser.add_argument('-k', dest='password', required=True, help='Shared secret password')



    parser.add_argument('-l', dest='listen_port', type=int, help='Server listen port')



    parser.add_argument('host', nargs ='?', help='Server IP address (client mode only)')

    parser.add_argument('port', nargs ='?', type=int, help='Server port (client mode only)')



    args = parser.parse_args()



    if args.listen_port:

        mode = 'server'

    elif args.host and args.port:

        mode = 'client'

    else:

        parser.error("You must specify either '-l PORT' (server) or 'HOST PORT' (client)")

    return mode, args



if __name__ == "__main__":

    mode, args = parse_args()

    password = args.password.encode()



    if mode == 'server':



        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

            server_socket.bind(('0.0.0.0', args.listen_port))

            server_socket.listen(1)



            conn, addr = server_socket.accept()

            with conn:

                salt = b''
                while len(salt) < 16:
                    chunk = conn.recv(16 - len(salt))
                    if not chunk:
                        raise ConnectionError("Connection closed while receiving salt")
                    salt += chunk

                length_bytes = b''
                while len(length_bytes) < 2:
                    chunk = conn.recv(2 - len(length_bytes))
                    if not chunk:
                        raise ConnectionError("Connection closed while receiving length")
                    length_bytes += chunk
                expected_length = unpack('>H', length_bytes)[0]

                payload = b''
                while len(payload) < expected_length:
                    chunk = conn.recv(expected_length - len(payload))
                    if not chunk:
                        raise ConnectionError("Connection closed while receiving payload")
                    payload += chunk

                
                if len(payload) < 32:

                    sys.stderr.write("Error: integrity check failed.\n")

                    sys.stderr.flush()

                    sys.exit(1)

                nonce = payload[:16]
                tag = payload[16:32]
                ciphertext = payload[32:]

                try:

                    key = PBKDF2(password, salt, dkLen=32)

                    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
                    plaintext = unpad(plaintext, AES.block_size)

                    print(f"Decrypted plaintext length {len(plaintext)} bytes", file=sys.stderr)



                    with open("decrypted_output.txt", "wb") as f:

                        f.write(plaintext)

                    sys.stdout.buffer.write(plaintext)

                    sys.stdout.buffer.flush()

           

                except (ValueError, KeyError):

                     sys.stderr.write("Error: integrity check failed.\n")

                     sys.stderr.flush()

                     sys.exit(1)

    

    elif mode == 'client':



        salt = get_random_bytes(16)

        key = PBKDF2(password, salt, dkLen=32)



        plaintext = sys.stdin.buffer.read()

        plaintext = pad(plaintext, AES.block_size)

        nonce = get_random_bytes(16)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        



        ciphertext, tag = cipher.encrypt_and_digest(plaintext)



        payload = nonce + tag + ciphertext

        length_bytes = pack('>H', len(payload))



        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect((args.host, args.port))

            s.sendall(salt + length_bytes + payload)

