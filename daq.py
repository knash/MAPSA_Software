
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
	
if options.readout=="counters":
	count=1
help	=	'readout which data ie counters, memory, both')

curconf.upload()
mapsa.daq().Strobe_settings(snum,sdel,slen,sdist)
if True
		self._calib.write(1)
		self._read.write(0)
		self._data_continuous.write(0)
		self._buffers.write(1)

			mapsa.daq().Shutter_open(smode,sdur)

			#time.sleep(.001)
			mapsa.daq().start_readout(1,0x0)
			pix,mem = mpa[mpa_index].daq().read_data(1)
			pix.pop(0)
			pix.pop(0)
			x1.append(x)
			y1.append(array('d',pix))
			print pix
			#print mem
			print ""
			time.sleep(0.01)
	
print x1
print y1

print "Generating nominal per pixel thdac values"
calibconf = mpa[mpa_index].config(xmlfile="data/Conf_default_MPA"+str(mpa_number)+"_config1.xml")
thdacv = []
#gr1 = []
for iy1 in range(0,len(y1[:][0])-1):
		#gr1.append(TGraph(len(x1)-1,x1,y1[iy1]))
		#if iy1==0:
		#	gr1[iy1].draw()
		#else:
		#	gr1[iy1].draw('same')


		plt.plot(x1,y1[:,iy1], '-') 
		plt.xlabel('Threshold DAC Value')
		plt.ylabel('Counter Value')	
		plt.show()	


		halfmax = max(y1[:][iy1])/2.0
		maxbin = y1[:][iy1].index(max(y1[:][iy1]))
		for ibin in range(0,len(x1)-1):
			print y1[:][0]
			print iy1
			print ibin
			xval = x1[ibin]
			xval1 = x1[ibin+1]
			yval = y1[ibin][iy1]
			yval1 = y1[ibin+1][iy1]
			print (yval-halfmax)
			print (yval1-halfmax)
			print 

			if yval1-halfmax<0.0 and ibin>maxbin:
				if abs(yval-halfmax)<(yval1-halfmax):
					thdacv.append(xval)
				else:
					thdacv.append(xval1)
				if iy1%2==0:
					calibconf.modifypixel((iy1)/2+1,'TRIMDACL',int(thdacv[iy1]) )
				else:
					calibconf.modifypixel((iy1+1)/2,'TRIMDACR', int(thdacv[iy1]))
				break	


print thdacv

xmlrootfile = calibconf.xmltree
xmlrootfile.write("data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
print "Testing Calibration"
calibconf = mpa[mpa_index].config(xmlfile="data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
calibconf.upload()
x1 = array('d')
y1 = []
for x in range(0,256):
			if x%1!=0:
				continue
			print "THDAC " + str(x)
			calibconf.modifyperiphery('THDAC',x)
			calibconf.upload()
			time.sleep(.01)
			print x

			mapsa.daq().Shutter_open(smode,sdur)

			#time.sleep(.001)
			mapsa.daq().start_readout(1,0x0)
			pix,mem = mpa[mpa_index].daq().read_data(1)
			pix.pop(0)
			pix.pop(0)
			x1.append(x)
			y1.append(array('d',pix))
			print pix
			#print mem
			print ""
			time.sleep(0.1)
	
print x1
print y1

print ""
print "Done"
