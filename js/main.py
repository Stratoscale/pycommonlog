import shutil
import argparse
import os
import subprocess
import SimpleHTTPServer
import SocketServer
import socket

parser = argparse.ArgumentParser( description = 'Present summary of tests results in a webpage.' )
parser.add_argument("--root", default="logs.racktest")
parser.add_argument("--whiteboxRoot", action="store_true")
parser.add_argument("--noBrowser", help="avoid openning the browser", action="store_true")
parser.add_argument("--noServer", action="store_true")
args = parser.parse_args()

if args.whiteboxRoot:
    args.root = "logs.whiteboxtest"

root = args.root
reporterDir = os.path.join(root, "_reporter")
originalReporterDir = "../pycommonlog/js"
shutil.rmtree(reporterDir, ignore_errors=True)
shutil.copytree(originalReporterDir, reporterDir)


class ReusingTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


if not args.noServer:
    os.chdir(args.root)
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = ReusingTCPServer(("127.0.0.1", PORT), Handler)
    BROWSER_CMDLINE = ["google-chrome", "http://127.0.0.1:8000/_reporter/index.html"]
    if not args.noBrowser:
        subprocess.Popen(BROWSER_CMDLINE)
    httpd.serve_forever()
