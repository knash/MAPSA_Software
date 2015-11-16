
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
import ROOT
from ROOT import TH2F, TCanvas, TTree, TBranch, TFile
#from ROOT import TGraph
import sys, select, os, array,subprocess
from array import array
#import ROOT
#from ROOT import TGraph
import datetime
saveout = sys.stdout
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
default	=	90,
dest	=	'thresh',
help	=	'threshold')


parser.add_option('-T', '--testclock', metavar='F', type='int', action='store',
default	=	1,
dest	=	'testclock',
help	=	'threshold')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	4000,
dest	=	'number',
help	=	'number of calcstrobe pulses to send')




parser.add_option('-x', '--record', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'record',
help	=	'record this daq cycle')

parser.add_option('-y', '--daqstring', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'daqstring',
help	=	'string to append on daq folder name')

parser.add_option('-z', '--monitor', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'monitor',
help	=	'start event monitor in background')


parser.add_option('-w', '--shutterdur', metavar='F', type='int', action='store',
default	=	0xFFFFF,
dest	=	'shutterdur',
help	=	'shutter duration')


parser.add_option('-v', '--skip', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'skip',
help	=	'skip zero counts')

parser.add_option('-u', '--autospill', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'autospill',
help	=	'write every spill')

parser.add_option('-N', '--norm', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'norm',
help	=	'write every spill')


(options, args) = parser.parse_args()

sys.stdout = saveout


daqver=1



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
firmver = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(firmver)



smode = 0x1
sdur = options.shutterdur

snum = options.number
sdel = 0xFFF
slen = 0xFFF
sdist = 0xFF


quickplot = TH2F("quickplot", "", 4,-0.5,3.5, 16, 0, 16 )

formarr = ['stubfinding','stripemulator' ,'centroid','noprocessing']
memmode = formarr.index(options.format)

a._hw.getNode("Control").getNode("logic_reset").write(0x1)
a._hw.dispatch()
a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
a._hw.dispatch()

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


pmap=[[1,1],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,10],[1,11],[1,12],[1,13],[1,14],[1,15],[1,16],[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[2,11],[2,12],[2,13],[2,14],[2,15],[2,16],[3,1],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[3,12],[3,13],[3,14],[3,15],[3,16]]

cntsperspill = 0.
startrun=True


if options.norm == 'False':
	thdac = [options.thresh,options.thresh,options.thresh,options.thresh,options.thresh,options.thresh]
else:
	thdac = [options.thresh,90,options.thresh,90,options.thresh,90]
Endloop = False
spillnumber = 0
if options.setting == 'default' or options.setting == 'calibration':

	mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,sdur)
	if options.autospill == 'True':
		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")
	
	while Endloop == False:
	    Endspill = False
	    startrun=True
	    while Endspill == False:
		zeroshutters=0
		cntsperspill = 0
		startrun=True
		spillnumber+=1
		sys.stdout = saveout
		print "Starting spill " + str(spillnumber)
	#	conffile = "data/Conf_calibrated_MPA"+str(mpa_number)+"_config1.xml"

		if options.record=='True':

			timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
			foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr+"_spill_"+str(spillnumber)
			commands = []
			commands.append('mkdir daqlogs')

			commands.append('mkdir daqlogs/'+foldername)
			commands.append('cp -r data daqlogs/'+foldername)
			logfname = 'daqlogs/'+foldername+'/log_'+timestr+'.log'

			if options.monitor=='True':
				commands.append('python show.py '+logfname+' &')
			for s in commands :
				print 'executing ' + s
				subprocess.call( [s], shell=True )
			tree_vars = {}
			for i in range(0,6):
					tree_vars["AR_MPA_"+str(i)] = array('L',[0]*48)
					if options.readout=='both':
						tree_vars["SR_BX_MPA_"+str(i)] = array('L',[0]*96)
						tree_vars["SR_MPA_"+str(i)] = array('L',[0]*96)
			F = TFile('daqlogs/'+foldername+'/output.root','recreate')
			tree=TTree("Tree","Tree")


			for key in tree_vars.keys():
				if "SR" in key:
					tree.Branch(key,tree_vars[key],key+"[96]/l")
				if "AR" in key:
					tree.Branch(key,tree_vars[key],key+"[48]/l")
				
	
			Outf1 = open(logfname, 'w')

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
			print "---------------------------------------------------------------------------"
			print "----------------------------Starting Datataking----------------------------"
			print "---------------------------------------------------------------------------"
			print 
		else:	
			Outf1 = saveout




		config = mapsa.config(Config=1,string='calibrated')
		config.upload()


		config.modifyperiphery('OM',[memmode]*6)
		#config.modifyperiphery('RT',[0]*6)
		#config.modifyperiphery('SCW',[0]*6)
		#config.modifyperiphery('SH2',[0]*6)
		#config.modifyperiphery('SH1',[0]*6)
		config.modifyperiphery('THDAC',thdac)
		config.modifyperiphery('CALDAC', [options.charge]*6)
		for x in range(1,25):
			#config.modifypixel(x,'PML', [1]*6)
			config.modifypixel(x,'ARL', [AR]*6)
			config.modifypixel(x,'CEL', [CE]*6)
			#config.modifypixel(x,'CW', [0]*6)
			#config.modifypixel(x,'PMR', [1]*6)
			config.modifypixel(x,'ARR', [AR]*6)
			config.modifypixel(x,'CER', [CE]*6)
			config.modifypixel(x,'SP',  [0]*6) 
			config.modifypixel(x,'SR',  [SR]*6) 

	
		config.write()





		while True:

     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] :
        			line = raw_input()
				print "Ending loop"
	    			Endspill = True
	    			Endloop = True
        			break
			if zeroshutters>=20:
				print "Spill "+str(spillnumber)
	    			Endspill = True
				if options.autospill == 'False':
					Endloop = True
        			break
			shutters+=1
			print 
			print "---------------------------------------------------------------------------"
			print "Total shutters "+str(shutters)
			sys.stdout = saveout
			print "Total shutters "+str(shutters)
			sys.stdout = Outf1


			print "Timestamp: " + str(datetime.datetime.now().time().isoformat().replace(":","").replace(".",""))
			time.sleep(.001)
			mapsa.daq().Shutter_open(smode,sdur)
			time.sleep(.001)
			mapsa.daq().start_readout(rbuffer,readmode)
			time.sleep(.001)

			#print mem
			sys.stdout = saveout
			pix,mem = mapsa.daq().read_data(1,tb=0)
			sys.stdout = Outf1
			parray = []
			marray = []
			cntspershutter = 0
			for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)
					#print pix[i]
					parray.append(pix[i])

					sys.stdout = saveout
					marray.append(mpa[i].daq().read_memory(mem[i],memmode,tb=0))
					#print 
					sys.stdout = Outf1
					cntsperspill += sum(pix[i])
					cntspershutter += sum(pix[i])
			sys.stdout = saveout
			print cntsperspill
			#print zeroshutters
			print cntspershutter
			sys.stdout = Outf1
			if cntsperspill>100.:
				startrun=False
			if cntspershutter == 0 and options.skip=='True':
				sys.stdout = saveout
				#print startrun
				#print zeroshutters 
				#print cntspershutter
				#print 
				sys.stdout = Outf1

				if startrun==False:
					zeroshutters+=1
				continue
			if AR:
				print "Counter output"
				i=0
				temp_vars = {}
				for p in parray:
					sys.stdout = Outf1
					print p
					print ""
					sys.stdout = saveout

					temp_vars["AR_MPA_"+str(i)]=p

					i+=1

					
					#if sum(p)==0 and startrun==False and cntsperspill > 100:
					#	spillsignal+=1



				ipix=0

				#print cntsperspill
				sys.stdout = Outf1

			if SR:
				print "Memory output"
				#for i in range(0,len(formmem[0])):
				i=0
				for memo in marray:
					print "BX:"+str(memo[0])
					print "Data:"+str(memo[1])
					print ""

					sys.stdout = saveout

					BXmemo = np.array(memo[0])	
					DATAmemo = np.array(memo[1])
					DATAmemoint = []	
					for DATAmem in DATAmemo:
						DATAmemoint.append(long(DATAmem,2)) 
						
						#print DATAmem
						#print long(DATAmem,2)
						#print
					#print DATAmemoint
					#print BXmemo
					temp_vars["SR_BX_MPA_"+str(i)]=BXmemo
					temp_vars["SR_MPA_"+str(i)]=DATAmemoint

					sys.stdout = Outf1
					i+=1
			for tv in tree_vars.keys():
				sys.stdout = saveout
				#print tv
				#print temp_vars[tv]
				#print 
				for i in range(0,len(temp_vars[tv])):
					tree_vars[tv][i] = temp_vars[tv][i]
	
				sys.stdout = Outf1

			tree.Fill()

			print "---------------------------------------------------------------------------"
		

	    F.Write()
	    F.Close()
if options.setting == 'testbeam':

		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")


		if options.record=='True':

			timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
			foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr+"_spill_"+str(spillnumber)
			commands = []
			commands.append('mkdir daqlogs')

			commands.append('mkdir daqlogs/'+foldername)
			commands.append('cp -r data daqlogs/'+foldername)
			logfname = 'daqlogs/'+foldername+'/log_'+timestr+'.log'

			if options.monitor=='True':
				commands.append('python show.py '+logfname+' &')
			for s in commands :
				print 'executing ' + s
				subprocess.call( [s], shell=True )
			tree_vars = {}
			tree_vars["TRIG_COUNTS_SHUTTER"] = array('L',[0])
			tree_vars["TRIG_COUNTS_TOTAL"] = array('L',[0])
			tree_vars["TRIG_OFFSET_BEAM"] = array('L',[0]*2048)
			tree_vars["TRIG_OFFSET_MPA"] = array('L',[0]*2048)
			for i in range(0,6):
					tree_vars["AR_MPA_"+str(i)] = array('L',[0]*48)

					if options.readout=='both':
						tree_vars["SR_BX_MPA_"+str(i)] = array('L',[0]*96)
						tree_vars["SR_MPA_"+str(i)] = array('L',[0]*96)
			F = TFile('daqlogs/'+foldername+'/output.root','recreate')
			tree=TTree("Tree","Tree")


			for key in tree_vars.keys():
				if "SR" in key:
					tree.Branch(key,tree_vars[key],key+"[96]/l")
				if "AR" in key:
					tree.Branch(key,tree_vars[key],key+"[48]/l")
				if "TRIG_OFFSET" in key:
					tree.Branch(key,tree_vars[key],key+"[2048]/l")
				if "TRIG_COUNTS" in key:
					tree.Branch(key,tree_vars[key],key+"[1]/l")
			Outf1 = open(logfname, 'w')

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
			print "---------------------------------------------------------------------------"
			print "----------------------------Starting Datataking----------------------------"
			print "---------------------------------------------------------------------------"
			print 
		else:	
			Outf1 = saveout


		config = mapsa.config(Config=1,string='calibrated')
		config.upload()


		config.modifyperiphery('OM',[memmode]*6)
		#config.modifyperiphery('RT',[0]*6)
		#config.modifyperiphery('SCW',[0]*6)
		#config.modifyperiphery('SH2',[0]*6)
		#config.modifyperiphery('SH1',[0]*6)
		config.modifyperiphery('THDAC',thdac)
		config.modifyperiphery('CALDAC', [options.charge]*6)
		for x in range(1,25):
			#config.modifypixel(x,'PML', [1]*6)
			config.modifypixel(x,'ARL', [AR]*6)
			config.modifypixel(x,'CEL', [CE]*6)
			#config.modifypixel(x,'CW', [0]*6)
			#config.modifypixel(x,'PMR', [1]*6)
			config.modifypixel(x,'ARR', [AR]*6)
			config.modifypixel(x,'CER', [CE]*6)
			config.modifypixel(x,'SP',  [0]*6) 
			config.modifypixel(x,'SR',  [SR]*6) 

	
		config.write()



		a._hw.getNode("Shutter").getNode("time").write(options.shutterdur)
		a._hw.dispatch()

		
		time.sleep(.2)
		a._hw.getNode("Control").getNode('testbeam_clock').write(options.testclock)
		a._hw.getNode("Control").getNode('testbeam_mode').write(0x1)
		a._hw.dispatch()



		ibuffer=1
		
		iread=0
		cntsperspill = 0
		while True:
	  

			buffers_num = a._hw.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
			spill = a._hw.getNode("Control").getNode('Sequencer').getNode('spill').read()
			a._hw.dispatch()

			if buffers_num<4:	
				shutters+=1
				iread+=1
				sys.stdout = saveout
				pix,mem = mapsa.daq().read_data(ibuffer,tb=1)
				sys.stdout = Outf1
				total_triggers = a._hw.getNode("Control").getNode('total_triggers').read()
				trigger_counter = a._hw.getNode("Control").getNode('trigger_counter').getNode('buffer_'+str(ibuffer)).read()
				Offset_BEAM = a._hw.getNode("Control").getNode('trigger_offset_BEAM').getNode('buffer_'+str(ibuffer)).readBlock(2048)
				Offset_MPA = a._hw.getNode("Control").getNode('trigger_offset_MPA').getNode('buffer_'+str(ibuffer)).readBlock(2048)
				a._hw.dispatch()


				parray = []
				marray = []
				cntspershutter = 0
				for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)
					#print pix[i]
					parray.append(pix[i])
					cntspershutter+=sum(pix[i])
					sys.stdout = saveout
					marray.append(mpa[i].daq().read_memory(mem[i],memmode,tb=1))
					#print 
					sys.stdout = Outf1
				cntsperspill+=cntspershutter
				sys.stdout = saveout
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Triggers Total: " + str(total_triggers)
				print "Counts per Shutter: " + str(cntspershutter)
				print "Triggers per Shutter: " + str(trigger_counter)	
				print "Reading buffer: " + str(ibuffer)
				print 
				sys.stdout = Outf1
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Triggers Total: " + str(total_triggers)
				print "Counts per Shutter: " + str(cntspershutter)
				print "Triggers per Shutter: " + str(trigger_counter)	
				print "Reading buffer: " + str(ibuffer)

				print 
				ibuffer+=1
				if ibuffer >4:
					ibuffer=1 
				offsetbeam = []
				offsetmpa = []
				offdat = []
				for i in range(0,trigger_counter):
					offsetbeam.append(Offset_BEAM[i])
					offdat.append(1000*(Offset_BEAM[i]-Offset_BEAM[0])/26.5)
					offsetmpa.append(Offset_MPA[i])

				print "Offset beam: " + str(offsetbeam)
				print "Offset mpa: " + str(offsetmpa)
				a._hw.dispatch()
				offset = []
				#for i in range(0,trigcount):
				#	offset.append(Offset_MPA[i])
				sys.stdout = saveout

				if AR:
					print "Counter output"
					i=0
					temp_vars = {}
					for p in parray:
						sys.stdout = Outf1
						print p
						print ""
						sys.stdout = saveout

						temp_vars["AR_MPA_"+str(i)]=p

						i+=1

					
					#if sum(p)==0 and startrun==False and cntsperspill > 100:
					#	spillsignal+=1


	
					ipix=0

					#print cntsperspill
					sys.stdout = Outf1

				if SR:
					print "Memory output"

					i=0
					for memo in marray:
						print "BX:"+str(memo[0])
						print "Data:"+str(memo[1])
						print ""

						sys.stdout = saveout

						BXmemo = np.array(memo[0])	
						DATAmemo = np.array(memo[1])
						DATAmemoint = []	
						for DATAmem in DATAmemo:
							DATAmemoint.append(long(DATAmem,2)) 
			
						temp_vars["SR_BX_MPA_"+str(i)]=BXmemo
						temp_vars["SR_MPA_"+str(i)]=DATAmemoint

						sys.stdout = Outf1
						i+=1

				temp_vars["TRIG_COUNTS_SHUTTER"] = [trigger_counter]
				temp_vars["TRIG_COUNTS_TOTAL"] = [total_triggers]
				temp_vars["TRIG_OFFSET_BEAM"] = offsetbeam
				temp_vars["TRIG_OFFSET_MPA"] = offsetmpa

				for tv in tree_vars.keys():
					sys.stdout = saveout

					#print tv
					#print temp_vars[tv]

	
					for i in range(0,len(temp_vars[tv])):
						tree_vars[tv][i] = temp_vars[tv][i]
	
					sys.stdout = Outf1

				tree.Fill()

				print "---------------------------------------------------------------------------"

			#mapsa.daq().start_readout(rbuffer,readmode)
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				a._hw.getNode("Control").getNode('testbeam_mode').write(0x0)
        			line = raw_input()
				print "Ending loop"
        			break

	        F.Write()
	        F.Close()

print ""
print "Done"
