
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
import ROOT
from ROOT import TH2F, TCanvas
#from ROOT import TGraph
import sys, select, os, array,subprocess
from array import array
#import ROOT
#from ROOT import TGraph
import datetime

from optparse import OptionParser
parser = OptionParser()

parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'calibration',
dest	=	'setting',
help	=	'settings ie default, calibration, testbeam etc')

parser.add_option('-r', '--readout', metavar='F', type='string', action='store',
default	=	'both',
dest	=	'readout',
help	=	'readout which data ie counters, memory, both')

parser.add_option('-f', '--format', metavar='F', type='string', action='store',
default	=	'noprocessing',
dest	=	'format',
help	=	'memout format noprocessing, stubfinding, centroid, stripemulator ')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	1,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')



parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	40,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-t', '--thresh', metavar='F', type='int', action='store',
default	=	100,
dest	=	'thresh',
help	=	'threshold')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1200,
dest	=	'number',
help	=	'number of calstrobe pulses to send')




parser.add_option('-x', '--record', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'record',
help	=	'record this daq cycle')

parser.add_option('-y', '--daqstring', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'daqstring',
help	=	'string to append on daq folder name')

parser.add_option('-z', '--monitor', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'monitor',
help	=	'start event monitor in background')


(options, args) = parser.parse_args()

daqver=1

saveout = sys.stdout

a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
firmver = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(firmver)

smode = 0x1
sdur = 0xFFFFFFFF

snum = options.number
sdel = 0xFFFF
slen = 5
sdist = 0xFFF

quickplot = TH2F("quickplot", "", 4,-0.5,3.5, 16, 0, 16 )

formarr = ['stubfinding','stripemulator' ,'centroid','noprocessing']
memmode = formarr.index(options.format)



mpa_number = options.mpa
mpa_index = mpa_number-1
nmpas=1

mpa = []  
for i in range(1,7):
		mpa.append(mapsa.getMPA(i))



rbuffer=1
timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")

if options.daqstring!='':
	dstr= '_'+options.daqstring

foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr

CE=0
if options.setting == 'calibration':
	CE=1
if options.readout=='both':
	AR=1
	SR=1
	readmode = 0x1
if options.readout=='counters':
	AR=1
	SR=0
	readmode = 0x0
if options.readout=='memory':
	AR=0
	SR=1
	readmode = 0x1

shutters=0
mapsa.daq().Strobe_settings(snum,sdel,slen,sdist)

pmap=[[1,1],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,10],[1,11],[1,12],[1,13],[1,14],[1,15],[1,16],[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[2,11],[2,12],[2,13],[2,14],[2,15],[2,16],[3,1],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[3,12],[3,13],[3,14],[3,15],[3,16]]

if options.setting == 'default' or options.setting == 'calibration':
		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")


		conffile = "data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml"

		if options.record=='True':
			commands = []
			commands.append('mkdir daqlogs')

			commands.append('mkdir daqlogs/'+foldername)
			commands.append('cp -r data daqlogs/'+foldername)

			for s in commands :
				print 'executing ' + s
				subprocess.call( [s], shell=True )
			logfname = 'daqlogs/'+foldername+'/log_'+timestr+'.log'
			Outf1 = open(logfname, 'w')
			if options.monitor==True:
				commands.append('python monitor.py -f logfname -s last &')
			sys.stdout = Outf1
			print "Firmware Version " + str(firmver)
			print "DAQ Version " + str(daqver)
			print 
			print "Options summary"
			print "=================="
			for opt,value in options.__dict__.items():
				print str(opt) +': '+ str(value)
			print "=================="
			print 
			print 'Configuration: ' + conffile
			print 
			print "---------------------------------------------------------------------------"
			print "----------------------------Starting Datataking----------------------------"
			print "---------------------------------------------------------------------------"
			print 
		else:	
			Outf1 = saveout
		curconf = mpa[mpa_index].config(xmlfile=conffile)
		curconf.modifyperiphery('OM',memmode)
		#curconf.modifyperiphery('RT',0)
		#curconf.modifyperiphery('SCW',0)
		#curconf.modifyperiphery('SH2',0)
		#curconf.modifyperiphery('SH1',0)
		curconf.modifyperiphery('THDAC',options.thresh)
		curconf.modifyperiphery('CALDAC', options.charge)
		for x in range(1,25):
			#curconf.modifypixel(x,'PML', 1)
			curconf.modifypixel(x,'ARL', AR)
			curconf.modifypixel(x,'CEL', CE)
			#curconf.modifypixel(x,'CW', 0)
			#curconf.modifypixel(x,'PMR', 1)
			curconf.modifypixel(x,'ARR', AR)
			curconf.modifypixel(x,'CER', CE)
			curconf.modifypixel(x,'SP',  0) 
			curconf.modifypixel(x,'SR',  SR) 

		curconf.upload(dcindex=1)

		while True:
			shutters+=1
			print 
			print "---------------------------------------------------------------------------"
			print "Total shutters "+str(shutters)
			sys.stdout = saveout
			print "Total shutters "+str(shutters)
			sys.stdout = Outf1


			print "Timestamp: " + str(datetime.datetime.now().time().isoformat().replace(":","").replace(".",""))
			time.sleep(.1)

			mapsa.daq().Shutter_open(smode,sdur)
			mapsa.daq().start_readout(rbuffer,readmode)

			pix,mem = mpa[mpa_index].daq().read_data(rbuffer,dcindex=1)


			pix.pop(0)
			pix.pop(0)

			sys.stdout = saveout
			print pix
			#print mem
			sys.stdout = Outf1


			if AR:
				print "Counter output"
				print pix
				print ""
				ipix=0
				for p in pix:

					sys.stdout = saveout
					#print "ipix " + str(ipix)
					xbin = quickplot.GetXaxis().FindBin(pmap[ipix][0])
					ybin = quickplot.GetYaxis().FindBin(pmap[ipix][1])

					if True:#ipix not in [3,5,6,25,27,28,29,30,31,35]:


						currcont = quickplot.GetBinContent(xbin,ybin)
						quickplot.SetBinContent(xbin,ybin,p+currcont)
					ipix+=1
					


					sys.stdout = Outf1


			if SR:
				print "Memory output"
				formmem =  mpa[mpa_index].daq().read_memory(mem,memmode)
				#for i in range(0,len(formmem[0])):
				print "BX:"+str(formmem[0])
				print "Data:"+str(formmem[1])
				print ""
				



			print "---------------------------------------------------------------------------"
		

     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or shutters==1000:
        			line = raw_input()
				print "Ending loop"
        			break

c2 = TCanvas('c2', '', 700, 600)

quickplot.Draw('colz')
c2.Print('plots/quickplot.root', 'root')
if options.setting == 'testing':


		curconf = mpa[mpa_index].config(xmlfile="data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml")
		curconf.modifyperiphery('OM',3)
		curconf.modifyperiphery('RT',0)
		curconf.modifyperiphery('SCW',0)
		curconf.modifyperiphery('SH2',0)
		curconf.modifyperiphery('SH1',0)
		curconf.modifyperiphery('THDAC',options.thresh)
		curconf.modifyperiphery('CALDAC', options.charge)
		for x in range(1,25):
			if x<=6:
				curconf.modifypixel(x,'PML', 1)
				curconf.modifypixel(x,'PMR', 1)
			else:
				curconf.modifypixel(x,'PML', 1)
				curconf.modifypixel(x,'PMR', 1)
			curconf.modifypixel(x,'ARL', 0)
			curconf.modifypixel(x,'CEL', 1)
			curconf.modifypixel(x,'CW', 00)
			curconf.modifypixel(x,'ARR', 0)
			curconf.modifypixel(x,'CER', 1)
			curconf.modifypixel(x,'SP',  0) 
			curconf.modifypixel(x,'SR',  1) 

		curconf.upload(dcindex=1)


		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")
		#write = a._hw.getNode("Control").getNode("Sequencer").getNode("buffers_index").write(0x1)
		#a._hw.dispatch()
		while True:
			time.sleep(.05)

			print "delay"


			time.sleep(.05)

			mapsa.daq().Shutter_open(smode,sdur)
				
			read = a._hw.getNode("Control").getNode("Sequencer").getNode("buffers_num").read()
			a._hw.dispatch()
			print "free buffers " + str(read) 	
			while read==0:
					read = a._hw.getNode("Control").getNode("Sequencer").getNode("buffers_num").read()
					a._hw.dispatch()	
					print read
			mapsa.daq().start_readout(rbuffer,0x1)
		#	mapsa.daq().start_readout(rbuffer,0x1)
				#mapsa.daq().daqloop(shutterdur=100,calib=0,data_continuous=0,read=1,buffers=1,testbeamclock=1)

			pix,mem = mpa[mpa_index].daq().read_data(rbuffer,dcindex=1)
			pix.pop(0)
			pix.pop(0)
			for m in mem:
				print m
			print pix
			read = a._hw.getNode("Control").getNode("Sequencer").getNode("buffers_num").read()
			a._hw.dispatch()
			print "filled buffers " + str(read) 	
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
