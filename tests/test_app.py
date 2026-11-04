import http.client
import threading
from http.server import ThreadingHTTPServer

from dictate.app import MAX_CONTENT_LENGTH, make_handler

def test_server(tmp_path):
    received = []
    httpd = ThreadingHTTPServer(
        ("127.0.0.1", 0), make_handler(tmp_path, "tok", received.append)
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]

    def post(path, body=b"hi", headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        conn.request("POST", path, body=body, headers=headers or {})
        status = conn.getresponse().status
        conn.close()
        return status

    try:
        assert post("/?token=wrong") == 403
        assert post("/") == 403
        assert post("/?token=tok", body="hola".encode()) == 200
        assert received == ["hola"]
        too_big = {"Content-Length": str(MAX_CONTENT_LENGTH + 1)}
        assert post("/?token=tok", body=b"", headers=too_big) == 413
    finally:
        httpd.shutdown()
        httpd.server_close()
