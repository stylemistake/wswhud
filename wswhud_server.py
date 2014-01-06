#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import json, threading, sys, time, socket

proto_link = None
server = None
state = {
	"last_request": time.time() - 2.5,
	"last_update": 0
}

class Handler( BaseHTTPRequestHandler ):
	
	def log_message( self, format, *args ):
		return True

	## Catch "broken pipe" errors that otherwise cause a stack trace in the log.
	def catch_epipe( fn ):
		def ret( self, *args ):
			try:
				fn(self, *args)
			except socket.error, e:
				if e.errno != errno.EPIPE: raise
				print "wswhud_server: broken pipe"
		return ret
	handle = catch_epipe( BaseHTTPRequestHandler.handle )
	finish = catch_epipe( BaseHTTPRequestHandler.finish )

	def do_GET( self ):
		global state

		time_request = time.time()

		if self.path == "/items.json":
			while state["last_request"] > time.time() - 2.5:
				last_update = proto_link.get_last_update()
				if ( last_update > state["last_update"] ):
					state["last_update"] = last_update
					break
				time.sleep( 0.05 )
			state["last_request"] = time.time()
			output = json.dumps({
				"items": proto_link.get_items(),
				"state": proto_link.get_state(),
				"time_response": state["last_request"],
				"time_request": time_request,
				"latency_proto": proto_link.get_latency()
			})
			self.send_response( 200 )
			self.send_header( "Content-type", "application/json" )
			self.end_headers()
			self.wfile.write( output )
			return

		elif self.path == "/":
			self.path = "/index.html"

		try:
			sendReply = False
			if self.path.endswith(".html"):
				mimetype = "text/html"
				sendReply = True
			if self.path.endswith(".png"):
				mimetype = "image/png"
				sendReply = True
			if self.path.endswith(".js"):
				mimetype = "application/javascript"
				sendReply = True
			if self.path.endswith(".css"):
				mimetype = "text/css"
				sendReply = True
			if self.path.endswith(".map"):
				mimetype = "application/json"
				sendReply = True

			if sendReply == True:
				## Open the static file requested and send it
				f = open( curdir + sep + "res" + sep + self.path ) 
				self.send_response( 200 )
				self.send_header( "Content-type", mimetype )
				self.end_headers()
				self.wfile.write( f.read() )
				f.close()
			return
		except IOError:
			self.send_error( 404, "Not Found" )

def start_server( port = 44100 ):
	global server
	try:
		server = HTTPServer( ( "", port ), Handler )
		print "wswhud: running on port", port
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()

def start( port = 44100, proto = None ):
	global proto_link
	proto_link = proto
	srv = threading.Thread( target = start_server, kwargs = {
		"port": port
	})
	srv.daemon = True
	srv.start()

def stop():
	global server
	server.socket.close()
	server = None
