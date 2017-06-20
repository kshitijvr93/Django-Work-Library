# Revised for python 3.5.2 based on
# example from effbot.org/librarybook/simplehttpserver.htm
# This works pretty well-- browsing gets a nice list of dirs and files as links.
# clicking on a dir descends and shows lower level,
# clicking on a file downloads it. Nifty.
import http.server
import socketserver
# minimal web server.  serves files relative to the
# current directory.
PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
#end code...
