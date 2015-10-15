
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
help	=	'settings ie default, testbeam etc')

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
default	=	100,
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
mpa = []  
for i in range(1,7):
		mpa.append(mapsa.getMPA(i))


curconf = mpa[mpa_index].config(xmlfile="data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
curconf.modifyperiphery('OM',3)
curconf.modifyperiphery('RT',0)
curconf.modifyperiphery('SCW',0)
curconf.modifyperiphery('SH2',0)
curconf.modifyperiphery('SH1',0)
curconf.modifyperiphery('THDAC',33)
curconf.modifyperiphery('CALDAC', options.charge)
for x in range(1,25):
		curconf.modifypixel(x,'PML', 1)
		curconf.modifypixel(x,'ARL', 1)
		curconf.modifypixel(x,'CEL', 1)
		curconf.modifypixel(x,'CW', 0)
		curconf.modifypixel(x,'PMR', 1)
		curconf.modifypixel(x,'ARR', 1)
		curconf.modifypixel(x,'CER', 1)
		curconf.modifypixel(x,'SP',  0) 
		curconf.modifypixel(x,'SR',  1) 


curconf.upload()

shutters=0
if options.setting == 'default':
		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")
		mapsa.daq().Strobe_settings(snum,sdel,slen,sdist)

		while True:
			time.sleep(.1)

			mapsa.daq().Shutter_open(smode,sdur)
			mapsa.daq().start_readout(1,0x1)
			pix,mem = mpa[mpa_index].daq().read_data(1)


			pix.pop(0)
			pix.pop(0)
			print pix
			#print mem
			print ""
			print ""


			shutters+=1
			print "Total shutters "+str(shutters)
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        			line = raw_input()
				print "Ending loop"
        			break






print ""
print "Done"
