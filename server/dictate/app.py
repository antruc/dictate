import io
import pathlib
import threading
import time

import http.server
import socket
import socketserver
import ssl

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from PIL import Image
import pyperclip
import pyautogui
import segno


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
        url = f"https://{self.host}:{self.port}"

        out_stream = io.BytesIO()
        segno.make(url).save(out_stream, kind="png", border=0, scale=15)
        out_stream.seek(0)
        qr_code = Image.open(out_stream)

        qr_image = toga.Image(qr_code)

        url_label = toga.Label(
            url,
            style=Pack(flex=1, margin_top=13, margin_left=10),
        )
        close_button = toga.Button("Close", on_press=self.exit_app, style=Pack(flex=1))

        url_box.add(toga.ImageView(qr_image, style=Pack(width=50, height=50)))
        url_box.add(url_label)
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
        threading.Thread(target=self.init_server).start()

    def init_server(self):

        # Directory to serve
        serve = pathlib.Path(__file__).parent / "www"

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=serve, **kwargs)

            def do_POST(self):
                content_length = int(self.headers["Content-Length"])
                body = self.rfile.read(content_length).decode("utf-8")
                time.sleep(0.5)

                pyperclip.copy(body)  # Copy body to clipboard
                pyautogui.hotkey("ctrl", "v")  # Paste it
                self.send_response(200)
                self.end_headers()

                response = "Received"
                self.wfile.write(response.encode("utf-8"))

            def log_message(self, format, *args):
                return  # Silent mode

        cert_file = pathlib.Path(__file__).parent / "cert.pem"
        key_file = pathlib.Path(__file__).parent / "key.pem"

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

        try:
            with socketserver.TCPServer((self.host, self.port), Handler) as self.httpd:
                self.httpd.socket = ssl_context.wrap_socket(
                    self.httpd.socket, server_side=True
                )
                self.httpd.serve_forever()
        except OSError:
            pass

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
            sock.connect(("192.168.1.1", 1))
            ip = sock.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            sock.close()
        return ip


def main():
    return Dictate()
