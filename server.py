import http.server
import socketserver
import subprocess
import os
from urllib.parse import urlparse

PORT = 8000

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/login":
            # Call the app.py script (replace with your full path if necessary)
            try:
                subprocess.Popen(['python', 'app.py'])
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Login action executed")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        else:
            # Serve static files (HTML, CSS, JS, etc.)
            super().do_GET()

def run(server_class=http.server.HTTPServer, handler_class=RequestHandler):
    # If you're not serving HTML files, this line is not necessary
    # os.chdir("your_directory_with_html_files")  # Remove or comment this line
    httpd = server_class(("", PORT), handler_class)
    print(f"Server started on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
