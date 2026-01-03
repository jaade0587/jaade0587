#!/usr/bin/env python3

import sys
import socket

BUFFER_SIZE = 4096

def print_usage_and_exit():
    print("Usage:")
    print(" Server: uft -l PORT > output_file")
    print(" Client: uft SERVER_IP PORT < input_file")
    sys.exit(1)

def run_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(1)
        print(f"Server listening on port {port}...", file=sys.stderr)
        conn, addr = server_socket.accept()
        print(f"Connection accepted from {addr}", file=sys.stderr)
        with conn:
            while True:
                length_bytes = b''
                while len(length_bytes) < 2:
                    chunk = conn.recv(2 - len(length_bytes))
                    if not chunk:
                        print("Client closed connection. Ending server.", file=sys.stderr)
                        return
                    length_bytes += chunk
                
                length = int.from_bytes(length_bytes, 'big')

                data = b''
                while len(data) < length:
                    chunk = conn.recv(length - len(data))
                    if not chunk:
                        print("Client closed connection unexpectedly!", file=sys.stderr)
                        return
                    data += chunk

                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()

def run_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        while True:
            data = sys.stdin.buffer.read(BUFFER_SIZE)
            if not data:
                break
            length = len(data)
            length_bytes = length.to_bytes(2, 'big')

            client_socket.sendall(length_bytes)
            client_socket.sendall(data)
        client_socket.shutdown(socket.SHUT_WR)
        print("Finished sending file. Client exiting.")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '-l':
       # Server mode
       try:
           port = int(sys.argv[2])
       except ValueError:
           print_usage_and_exit()
       run_server(port)

    elif len(sys.argv) == 3:
        #Client mode
        host = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print_usage_and_exit()
        run_client(host, port)

    else:
         print_usage_and_exit()
    

if __name__ == "__main__":
    main()

