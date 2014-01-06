#!/usr/bin/python

## --------------------------------------------------------------------------
##   Pixelcode protocol for Warsow HUD
## --------------------------------------------------------------------------

import gtk, sys, time, random, string, threading, numpy


## --------------------------------------------------------------------------
##   Initialization
## --------------------------------------------------------------------------

gdk_root = gtk.gdk.get_default_root_window()
gdk_size = tuple( gdk_root.get_size() )
gdk_cm = gtk.gdk.colormap_get_system()
gdk_cs = gtk.gdk.COLORSPACE_RGB
gdk_pb = gtk.gdk.Pixbuf( gdk_cs, False, 8, 1, 1 )

state = {
	"pixcode_position": None,
	"last_update": time.time(),
	"last_decrease": time.time(),
	"match_running": True,
	"has_mega": False,
}

beacon = [
	[ 8, 16, 24 ],
	[ 16, 8, 24 ],
	[ 8, 24, 8 ],
	[ 24, 0, 8 ]
]

timers = {}
items = []

item_respawn_times = {
	"match_start": 15,
	"shell": 90,
	"quad": 90,
	"mega": 20,
	"ultra": 40,
	"red": 25,
	"yellow": 25,
	"green": 25,
	"h50": 15,
	"h25": 15,
}

item_pixcodes = {
	"_": ( 0, 0, 0 ),
	"ready": ( 128, 255, 255 ),
	"shell": ( 128, 0, 255 ),
	"quad": ( 255, 64, 0 ),
	"mega": ( 255, 0, 255 ),
	"ultra": ( 0, 0, 255 ),
	"red": ( 255, 0, 0 ),
	"yellow": ( 255, 255, 0 ),
	"green": ( 0, 255, 0 ),
	"h50": ( 255, 128, 0 ),
	"h25": ( 255, 192, 0 ),
}


## --------------------------------------------------------------------------
##   Custom classes
## --------------------------------------------------------------------------

class Timer( object ):
    def __init__( self, interval, function, *args, **kwargs ):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run( self ):
        self.is_running = False
        self.start()
        self.function( *self.args, **self.kwargs )

    def start( self ):
        if not self.is_running:
            self._timer = threading.Timer( self.interval, self._run )
            self._timer.start()
            self.is_running = True

    def stop( self ):
        self._timer.cancel()
        self.is_running = False


## --------------------------------------------------------------------------
##   Private methods
## --------------------------------------------------------------------------

def read_pixel( x, y ):
	gdk_pb.get_from_drawable( gdk_root, gdk_cm, x, y, 0, 0, 1, 1 )
	return tuple( gdk_pb.get_pixels_array().tolist()[0][0] )

def read_screen( scale = 2 ):
	pb  = gtk.gdk.Pixbuf( gdk_cs, False, 8, gdk_size[0], gdk_size[1] )
	pbq = gtk.gdk.Pixbuf( gdk_cs, False, 8, gdk_size[0]/scale, gdk_size[1]/scale )
	pb.get_from_drawable( gdk_root, gdk_cm, 0, 0, 0, 0, *gdk_size )
	pb.scale( pbq,
		0, 0, gdk_size[0]/scale, gdk_size[1]/scale,
		0, 0, 1.0/scale, 1.0/scale, gtk.gdk.INTERP_NEAREST
	)
	return pbq.get_pixels_array().tolist()

def find_pixcode( scale = 2 ):
	screen = read_screen( scale = scale )
	beacon_i = 0; beacon_x = [ 0, 0, 0, 0 ]
	for y in range( 0, len(screen) ):
		for x in range( 0, len(screen[0]) ):
			if screen[y][x] == beacon[ beacon_i ]:
				beacon_x[ beacon_i ] = x; beacon_i += 1
				if beacon_i == len( beacon ):
					target = ( beacon_x[0] - 1, y )
					return ( target[0] * scale + scale - 1, target[1] * scale + scale - 1 )
			elif ( beacon_i > 0 ) and ( screen[y][x] != beacon[ beacon_i - 1 ] ):
				beacon_i = 0
	return None

def decode_pixel( pixel ):
	if not pixel in item_pixcodes.values(): return None
	for k, v in item_pixcodes.items():
		if v == pixel: return k
	return None

def generate_id( size = 6, chars = string.ascii_lowercase + string.digits ):
	return ''.join( random.choice( chars ) for x in range( size ) )

def item_timers_add( items, item_name ):
	timers = [ x["timer"] for x in items if ( x["name"] == item_name ) ]
	if ( len( timers ) == 0 ) or ( max( timers ) < item_respawn_times[ item_name ] - 3 ):
		items.append({
			"id": generate_id(),
			"name": item_name,
			"timer": item_respawn_times[ item_name ],
			"time_picked": time.time(),
			"time_respawn": time.time() + item_respawn_times[ item_name ]
		})
		state["last_update"] = time.time()

def item_timers_decrease( items ):
	now = time.time()
	diff = round( now - state["last_decrease"] )
	if ( diff < 2 ): diff = 1
	#if ( now%1 >= 0 ) and ( now%1 < timer.interval ):
	for ( i, item ) in enumerate( items ):
		if item["timer"] > 0: items[i]["timer"] -= diff
	for item in items:
		if item["timer"] < 1: items.remove( item )
	state["last_decrease"] = state["last_decrease"] + diff


## --------------------------------------------------------------------------
##   Threads
## --------------------------------------------------------------------------

def main_thread():
	global state, items
	if state["pixcode_position"] == None: return False
	## Get dem pixel :3
	p = read_pixel( *state["pixcode_position"] )
	item = decode_pixel( p )
	## Special case for mega health
	if ( item == "mega" ):
		state["has_mega"] = True
		state["last_update"] = time.time()
	elif ( item == "_" ) and state["has_mega"]:
		state["has_mega"] = False
		item_timers_add( items, "mega" )
		state["last_update"] = time.time()
	## Special case for match start
	elif ( item == "ready" ):
		state["match_running"] = False
		items = []
		state["last_update"] = time.time()
	elif ( item != "ready" ) and not state["match_running"]:
		state["match_running"] = True
		items = []
		item_timers_add( items, "match_start" )
		state["last_update"] = time.time()
	## Everything else
	elif ( item != None ) and ( item != "_" ):
		item_timers_add( items, item )

def item_timer_thread():
	global state, items
	item_timers_decrease( items )


## --------------------------------------------------------------------------
##   Public API
## --------------------------------------------------------------------------

def start( freq = 8 ):
	global timers
	timers["main"] = Timer( 1.0/freq, main_thread )
	timers["item"] = Timer( 1.0, item_timer_thread )
	print "proto_pixcode: searching for pixcode beacon..."
	while True:
		position = find_pixcode()
		if position != None:
			state["pixcode_position"] = position
			print "proto_pixcode:", position, read_pixel( *position )
			break
		time.sleep( 1 )
	state["last_update"] = time.time()
	timers["main"].start()
	timers["item"].start()
	print "proto_pixcode: locked on! :)"

def stop():
	if len( timers ) > 0:
		timers["main"].stop()
		timers["item"].stop()

def get_items(): return items
def get_state(): return state
def get_last_update(): return state["last_update"]
def get_latency():
	if "main" in timers: return timers["main"].interval / 2
	else: return None
def test_put_item( item ): item_timers_add( items, item )
