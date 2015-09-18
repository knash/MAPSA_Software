
from classes import *
import sys, select, os

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-v', '--volt', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'volt',
help	=	'on or off')

(options, args) = parser.parse_args()



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)

if options.volt=='on':
	print "Voltage on..."
	mapsa.VDDPST_on()
	mapsa.DVDD_on()
	mapsa.AVDD_on()
	mapsa.PVDD_on()

elif options.volt=='off':
	print "Voltage off..."
	mapsa.PVDD_off()
	mapsa.AVDD_off()
	mapsa.DVDD_off()
	mapsa.VDDPST_off()

else:
	print "please specify voltage on or off"


print ""
print "Done"
