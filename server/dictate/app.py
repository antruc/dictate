import hmac
import io
import pathlib
import secrets
import socket
import ssl
import sys
import threading
import time

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import pyperclip
import pyautogui
import segno
from PIL import Image

# Maximum accepted POST body size (1 MB)
MAX_CONTENT_LENGTH = 1024 * 1024

# Paste shortcut modifier per platform
PASTE_MODIFIER = "command" if sys.platform == "darwin" else "ctrl"

# One global lock, a single user pastes one text at a time
_paste_lock = threading.Lock()


def paste_text(text):
    """Copy text to the clipboard, paste it, then restore the clipboard."""
    with _paste_lock:
        previous = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.2)  # Give the clipboard time to update
        pyautogui.hotkey(PASTE_MODIFIER, "v")
        time.sleep(0.2)  # Let the paste complete before restoring
        pyperclip.copy(previous)


def make_handler(directory, token, on_text):
    """Build a request handler that serves `directory` and accepts
    authenticated POSTs, passing the received text to `on_text`."""

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def do_POST(self):
            # Token rides the query string, the client posts to its
            # own URL so it needs zero client code. Header if that ever changes
            query = parse_qs(urlparse(self.path).query)
            received_token = query.get("token", [""])[0]
            if not hmac.compare_digest(received_token, token):
                self.send_error(403, "Invalid token")
                return

            # Validate Content-Length
            try:
                content_length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                self.send_error(411, "Content-Length required")
                return
            if content_length <= 0 or content_length > MAX_CONTENT_LENGTH:
                self.send_error(413, "Payload too large")
                return

            body = self.rfile.read(content_length).decode("utf-8", errors="replace")
            on_text(body)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Received")

        def log_message(self, format, *args):
            return  # Silent mode

    return Handler


class Dictate(toga.App):
    def startup(self):

        # Create Toga components
        main_box = toga.Box(style=Pack(direction=COLUMN))

        url_box = toga.Box(
            style=Pack(direction=ROW, margin_top=10, margin_right=10, margin_left=10)
        )
        buttons_box = toga.Box(style=Pack(direction=ROW, margin=10))

        self.host = self.get_local_ip()
        self.port = 4443
        self.token = secrets.token_urlsafe(16)
        url = f"https://{self.host}:{self.port}/?token={self.token}"

        out_stream = io.BytesIO()
        segno.make(url).save(out_stream, kind="png", border=0, scale=15)
        out_stream.seek(0)
        qr_code = Image.open(out_stream)

        qr_image = toga.Image(qr_code)

        self.url_label = toga.Label(
            f"https://{self.host}:{self.port}",
            style=Pack(flex=1, margin_top=13, margin_left=10),
        )
        close_button = toga.Button("Close", on_press=self.exit_app, style=Pack(flex=1))

        url_box.add(toga.ImageView(qr_image, style=Pack(width=50, height=50)))
        url_box.add(self.url_label)
        buttons_box.add(close_button)

        main_box.add(url_box)
        main_box.add(buttons_box)

        # Create and show main window
        self.main_window = toga.Window(
            size=toga.Size(180, 60), resizable=True, on_close=self.exit_app
        )
        self.main_window.content = main_box
        self.main_window.show()

        self.start_app()

    def start_app(self):
        threading.Thread(target=self.init_server, daemon=True).start()

    def init_server(self):

        # Directory to serve
        serve = pathlib.Path(__file__).parent / "www"

        handler = make_handler(serve, self.token, paste_text)

        cert_file = pathlib.Path(__file__).parent / "cert.pem"
        key_file = pathlib.Path(__file__).parent / "key.pem"

        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

            with ThreadingHTTPServer((self.host, self.port), handler) as self.httpd:
                self.httpd.socket = ssl_context.wrap_socket(
                    self.httpd.socket, server_side=True
                )
                self.httpd.serve_forever()
        except OSError as exc:
            # Port in use, missing cert/key, etc. Report it in the UI
            self.loop.call_soon_threadsafe(self.report_error, f"Server error: {exc}")

    def report_error(self, message):
        self.url_label.text = message

    def exit_app(self, widget):
        self.loop.call_soon_threadsafe(self.shutdown)

    def shutdown(self):
        try:
            self.httpd.shutdown()
            self.exit()
        except AttributeError:
            self.exit()

    def get_local_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0)
        try:
            # No packet is sent; this only selects the outbound interface
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            sock.close()
        return ip


def main():
    return Dictate()
