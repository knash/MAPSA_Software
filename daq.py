
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
#import ROOT
#from ROOT import TGraph
import sys, select, os, array
from array import array
#import ROOT
#from ROOT import TGraph


from optparse import OptionParser
parser = OptionParser()

parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'default',
dest	=	'setting',
help	=	'settings ie calibration, testbeam etc')

parser.add_option('-r', '--readout', metavar='F', type='string', action='store',
default	=	'both',
dest	=	'readout',
help	=	'readout which data ie counters, memory, both')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	1,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')

parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	50,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1000,
dest	=	'number',
help	=	'number of calstrobe pulses to send')



(options, args) = parser.parse_args()



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)

smode = 0x1
sdur = 0xFFFF

snum = options.number
sdel = 50
slen = 15
sdist = 50

mpa_number = options.mpa
mpa_index = mpa_number-1
	
print ""
print "Done"
