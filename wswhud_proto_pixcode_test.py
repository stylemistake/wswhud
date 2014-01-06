#!/usr/bin/python

import unittest
import wswhud_proto_pixcode as proto, time, sys


## --------------------------------------------------------------------------
##   Simple sequential test
## --------------------------------------------------------------------------

class TestSequenceFunctions( unittest.TestCase ):

	def test_decode_pixel( self ):
		for k, v in proto.item_pixcodes.items():
			self.assertEqual( proto.decode_pixel(v), k )
		self.assertEqual( proto.decode_pixel((12, 34, 56)), None )

	def test_item_timing( self ):
		proto.item_respawn_times["test"] = 3
		proto.item_timers_add( proto.items, "test" )
		proto.item_timers_add( proto.items, "ultra" )
		for i in range( 3 ):
			time.sleep( 1 );
			proto.item_timers_decrease( proto.items )
			sys.stderr.write(".")
		self.assertNotIn( "test", [ x["item"] for x in proto.items ] )
		self.assertIn( 37, [ x["timer"] for x in proto.items ] )

if __name__ == '__main__': unittest.main()
