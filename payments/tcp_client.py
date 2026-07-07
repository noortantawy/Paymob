import socket
import urllib.parse


def send_query(data, *, host, port, timeout):
    #Send ``data`` as a query string to ``host:port`` and return the reply.
    query_string = urllib.parse.urlencode(data)
    payload = (query_string + "\n").encode("utf-8")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.sendall(payload)
        with sock.makefile("r", encoding="utf-8") as reader:
            return reader.readline().strip()
