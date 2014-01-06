#!/usr/bin/python
import sys, time, threading, getopt
import wswhud_proto_pixcode
import wswhud_server


## --------------------------------------------------------------------------
##   Initialization
## --------------------------------------------------------------------------

## Default protocol
proto = wswhud_proto_pixcode

## Configuration
opts = {
	"port": 44100,
	"freq": 4
}


## --------------------------------------------------------------------------
##   Getting commandline options
## --------------------------------------------------------------------------

def print_help():
	print "Usage: wswhud_app <options>"; tab = "   "
	print "Options:"
	print tab, "-p --port <n>: Server port (default: 44100)"
	print tab, "-f --freq <n>: Protocol update frequency, in Hz (default: 4)"
	print tab, tab, "Higher value increases hud precision at cost of some game lag"
	print tab, tab, "Reasonable values are between 2-8"
	print tab, "-h --help: Display this help message"
	sys.exit(2)

try:
	getopt_opts, argv = getopt.getopt( sys.argv[1:], "+hp:f:", [
		"port=", "freq=", "help",
	])
except getopt.GetoptError:
	print "(error) invalid parameter(s)"; print_help()

for opt, arg in getopt_opts:
	if opt in ( "-p", "--port" ): opts["port"] = int( arg )
	if opt in ( "-f", "--freq" ): opts["freq"] = int( arg )
	if opt in ( "-h", "--help" ): print_help()


## --------------------------------------------------------------------------
##   Entry point
## --------------------------------------------------------------------------

try:
	print "wswhud: starting..."
	wswhud_server.start( proto = proto, port = opts["port"] )
	time.sleep( 1.0 )
	proto.start( freq = opts["freq"] )
	while True:
		# proto.test_put_item("red")
		# proto.test_put_item("mega")
		time.sleep( 10.0 )
except KeyboardInterrupt:
	print "\nwswhud: exiting..."
	wswhud_server.stop()
	proto.stop()
