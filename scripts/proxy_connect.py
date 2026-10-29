#!/usr/bin/env python3
"""ProxyCommand helper: CONNECT through the runtime proxy on the Tailscale port (3130).

Usage: proxy_connect.py <target-host> <target-port>
Reads HTTPS_PROXY from the environment, swaps its port to 3130 (the
Tailscale tunnel port), issues an HTTP CONNECT, then relays bytes between
the proxy socket and stdin/stdout for ssh.
"""
import base64
import os
import select
import socket
import sys
from urllib.parse import urlparse, unquote


def main() -> int:
    target_host, target_port = sys.argv[1], int(sys.argv[2])
    proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if not proxy_url:
        print("no HTTPS_PROXY in env", file=sys.stderr)
        return 1
    p = urlparse(proxy_url)
    proxy_host = p.hostname
    # Tailscale tunnel lives on the same proxy host, port 3130.
    proxy_port = 3130

    s = socket.create_connection((proxy_host, proxy_port), timeout=30)
    req = [f"CONNECT {target_host}:{target_port} HTTP/1.1",
           f"Host: {target_host}:{target_port}"]
    if p.username:
        creds = f"{unquote(p.username)}:{unquote(p.password or '')}"
        req.append("Proxy-Authorization: Basic " +
                   base64.b64encode(creds.encode()).decode())
    s.sendall(("\r\n".join(req) + "\r\n\r\n").encode())

    # Read response headers
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            print("proxy closed during CONNECT", file=sys.stderr)
            return 1
        buf += chunk
    head, _, rest = buf.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n")[0].decode(errors="replace")
    if " 200 " not in status_line and not status_line.endswith(" 200"):
        print(f"CONNECT failed: {status_line}", file=sys.stderr)
        return 1
    if rest:
        os.write(sys.stdout.fileno(), rest)

    s.setblocking(False)
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    fds = [s, stdin]
    while True:
        r, _, _ = select.select(fds, [], [])
        if s in r:
            try:
                data = s.recv(65536)
            except BlockingIOError:
                data = b""
            if not data:
                break
            stdout.write(data)
            stdout.flush()
        if stdin in r:
            data = os.read(stdin.fileno(), 65536)
            if not data:
                try:
                    s.shutdown(socket.SHUT_WR)
                except OSError:
                    pass
                fds.remove(stdin)
                if not fds:
                    break
                continue
            s.sendall(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
