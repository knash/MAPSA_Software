
from classes import *
import sys, select, os, array
from array import array
#import ROOT
#from ROOT import TGraph

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'default',
dest	=	'setting',
help	=	'configuration setting ie default')

parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1,
dest	=	'number',
help	=	'configuration number')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	1,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')

(options, args) = parser.parse_args()



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)

mpa_number = options.mpa
mpa_index = mpa_number-1
	
mpa = []  
for i in range(1,7):
		mpa.append(mapsa.getMPA(i))

Confnum=options.number
configarr = []

writesetting=6-mpa_number

print "Configuring MPA number " + str(mpa_number)

curconf = mpa[mpa_index].config(xmlfile="data/Conf_"+options.setting+"_MPA"+str(mpa_number)+"_config"+str(Confnum)+".xml")
curconf.upload()


print ""
print "Done"
