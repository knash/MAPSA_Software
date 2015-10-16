
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
#import ROOT
#from ROOT import TGraph
import sys, select, os, array
from array import array
import ROOT
from ROOT import TGraph, TCanvas, gPad

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.pyplot import show, plot

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	30,
dest	=	'charge',
help	=	'Charge for caldac')
parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1000,
dest	=	'number',
help	=	'number of calstrobe pulses to send')
parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	1,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')
parser.add_option('-r', '--res', metavar='F', type='int', action='store',
default	=	1,
dest	=	'res',
help	=	'resolution 1,2,3... 1 is best')
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
slen = 50
sdist = 50

buffnum=1

mpa_number = options.mpa
mpa_index = mpa_number-1
	
mpa = []  
for i in range(1,7):
		mpa.append(mapsa.getMPA(i))


Confnum=1
configarr = []

curconf = mpa[mpa_index].config(xmlfile="data/Conf_default_MPA"+str(mpa_number)+"_config1.xml")
curconf.modifyperiphery('OM',3)
curconf.modifyperiphery('RT',0)
curconf.modifyperiphery('SCW',0)
curconf.modifyperiphery('SH2',0)
curconf.modifyperiphery('SH1',0)
curconf.modifyperiphery('THDAC',0)
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



mapsa.daq().Strobe_settings(snum,sdel,slen,sdist)
x1 = array('d')
y1 = []
for x in range(0,256):
			if x%options.res!=0:
				continue
			if x%10==0:
				print "THDAC " + str(x)

			curconf.modifyperiphery('THDAC',x)
			curconf.upload()



			#mapsa.daq().daqloop(shutterdur=0,calib=1,data_continuous=0,read=0,buffers=buffnum,testbeamclock=0)

			mapsa.daq().Shutter_open(smode,sdur)
			mapsa.daq().start_readout(1,0x0)

			pix,mem = mpa[mpa_index].daq().read_data(buffnum)
			pix.pop(0)
			pix.pop(0)
			x1.append(x)
			y1.append(array('d',pix))
			#print pix
			#print ""
			time.sleep(0.001)
	
#print x1
#print y1

print "Generating nominal per pixel trimdac values"
calibconf = mpa[mpa_index].config(xmlfile="data/Conf_default_MPA"+str(mpa_number)+"_config1.xml")
calibconfxmlroot = mpa[mpa_index].config(xmlfile="data/Conf_default_MPA"+str(mpa_number)+"_config1.xml").xmlroot
thdacv = []
#gr1 = []
xvec =  np.array(x1)
yarr =  np.array(y1)
gr1 = []
c1 = TCanvas('c1', '', 700, 600)
for iy1 in range(0,len(yarr[0,:])-1):
		yvec = yarr[:,iy1]

		gr1.append(TGraph(len(x1)-1,array('d',xvec),array('d',yvec)))
		if iy1==0:
			gr1[iy1].SetTitle(';DAC Value (1.456 mV);Counts (1/1.456)')
			gr1[iy1].Draw()

		else:
			gr1[iy1].Draw('same')
			gPad.Update()


		#print xvec
		#print yvec
		#plt.plot(xvec,yvec, '-') 
		#plt.xlabel('Threshold DAC Value')
		#plt.ylabel('Counter Value')	
		#plt.show()	


		halfmax = max(yvec)/2.0
		maxbin = np.where(yvec==max(yvec))
		for ibin in range(0,len(xvec)-1):

			xval = xvec[ibin]
			xval1 = xvec[ibin+1]
			yval = yvec[ibin]
			yval1 = yvec[ibin+1]
	
			if yval1-halfmax<0.0 and ibin>maxbin[0][0]:
				if iy1%2==0:
					prev_trim = int(calibconfxmlroot[(iy1)/2+1].find('TRIMDACL').text)
				else:
					prev_trim = int(calibconfxmlroot[(iy1+1)/2].find('TRIMDACR').text)

				if abs(yval-halfmax)<(yval1-halfmax):
					xdacval = xval
				else:
					xdacval = xval1
				trimdac = int(31) + prev_trim - int(xdacval*1.456/3.75)
				print trimdac
				if trimdac<0:
					trimdac = int(0)					
				if iy1%2==0:
					calibconf.modifypixel((iy1)/2+1,'TRIMDACL',trimdac )
				else:
					calibconf.modifypixel((iy1+1)/2,'TRIMDACR',trimdac)
				thdacv.append(trimdac)
				break	
			if ibin==len(xvec)-2:
				if iy1%2==0:
					prev_trim = int(calibconfxmlroot[(iy1)/2+1].find('TRIMDACL').text)
				else:
					prev_trim = int(calibconfxmlroot[(iy1+1)/2].find('TRIMDACR').text)

				trimdac = int(prev_trim)
				if iy1%2==0:
					calibconf.modifypixel((iy1)/2+1,'TRIMDACL',trimdac )
				else:
					calibconf.modifypixel((iy1+1)/2,'TRIMDACR', trimdac)
				thdacv.append(trimdac)
				break	

print thdacv

c1.Print('plots/Scurve_Calibration_pre.root', 'root')
c1.Print('plots/Scurve_Calibration_pre.pdf', 'pdf')
c1.Print('plots/Scurve_Calibration_pre.png', 'png')





xmlrootfile = calibconf.xmltree
print "writing data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml"
xmlrootfile.write("data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
print "Testing Calibration"

curconf1 = mpa[mpa_index].config(xmlfile="data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
curconf1.upload()

curconf1.modifyperiphery('OM',3)
curconf1.modifyperiphery('RT',0)
curconf1.modifyperiphery('SCW',0)
curconf1.modifyperiphery('SH2',0)
curconf1.modifyperiphery('SH1',0)
curconf1.modifyperiphery('THDAC',0)
curconf1.modifyperiphery('CALDAC', options.charge)
for x in range(1,25):
		curconf1.modifypixel(x,'PML', 1)
		curconf1.modifypixel(x,'ARL', 1)
		curconf1.modifypixel(x,'CEL', 1)
		curconf1.modifypixel(x,'CW', 0)
		curconf1.modifypixel(x,'PMR', 1)
		curconf1.modifypixel(x,'ARR', 1)
		curconf1.modifypixel(x,'CER', 1)
		curconf1.modifypixel(x,'SP',  1) 
		curconf1.modifypixel(x,'SR',  0) 
curconf1.upload()

x1 = array('d')
y1 = []

for x in range(0,256):
			if x%options.res!=0:
				continue
			if x%10==0:
				print "THDAC " + str(x)

			curconf1.modifyperiphery('THDAC',x)
			curconf1.upload()

			#mapsa.daq().daqloop(shutterdur=0,calib=1,data_continuous=0,read=0,buffers=buffnum,testbeamclock=0)


			mapsa.daq().Shutter_open(smode,sdur)
			mapsa.daq().start_readout(1,0x0)

			pix,mem = mpa[mpa_index].daq().read_data(buffnum)
			pix.pop(0)
			pix.pop(0)
			x1.append(x)
			y1.append(array('d',pix))
			#print pix
			#print ""
			time.sleep(0.001)
	


xvec =  np.array(x1)
yarr =  np.array(y1)

#print xvec
#print yarr
gr2 = []
c2 = TCanvas('c2', '', 700, 600)
for iy1 in range(0,len(yarr[0,:])-1):
		yvec = yarr[:,iy1]

		gr2.append(TGraph(len(x1)-1,array('d',xvec),array('d',yvec)))
		if iy1==0:
			gr2[iy1].SetTitle(';DAC Value (1.456 mV);Counts (1/1.456)')
			gr2[iy1].Draw()

		else:
			gr2[iy1].Draw('same')
			gPad.Update()



c2.Print('plots/Scurve_Calibration_post.root', 'root')
c2.Print('plots/Scurve_Calibration_post.pdf', 'pdf')
c2.Print('plots/Scurve_Calibration_post.png', 'png')

print ""
print "Done"
