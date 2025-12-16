from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
import json
from datetime import datetime

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)) + '/logs', **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f"Server started at http://localhost:{port}")
    print("Open http://localhost:8000/report.html to view the dashboard")
    
    try:
        webbrowser.open(f'http://localhost:{port}/report.html')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
