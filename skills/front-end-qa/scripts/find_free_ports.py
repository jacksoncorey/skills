#!/usr/bin/env python3
"""
Find N free local ports, starting at 4100, and print them space-separated.

Usage:
    python find_free_ports.py [count]

Reserves all ports in one call (rather than finding them one at a time) so a
third process can't grab a port between two separate checks.
"""
import socket
import sys


def is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_free_ports(count: int, start: int = 4100, end: int = 4999) -> list[int]:
    found: list[int] = []
    for port in range(start, end):
        if is_free(port) and port not in found:
            found.append(port)
            if len(found) == count:
                return found
    raise RuntimeError(f"Could not find {count} free ports in range {start}-{end}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    ports = find_free_ports(n)
    print(" ".join(str(p) for p in ports))
