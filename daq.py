
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
default	=	'default',
dest	=	'setting',
help	=	'settings ie default,  testbeam etc')

parser.add_option('-C', '--calib', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'calib',
help	=	'calibration')

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
default	=	80,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-t', '--thresh', metavar='F', type='int', action='store',
default	=	90,
dest	=	'thresh',
help	=	'threshold')


parser.add_option('-T', '--testclock', metavar='F', type='int', action='store',
default	=	1,
dest	=	'testclock',
help	=	'test beam clock')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	0xF,
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
help	=	'use normalization mpa scheme')


(options, args) = parser.parse_args()

sys.stdout = saveout


daqver=1



a = uasic(connection="file://connections_test.xml",device="board0")
mapsa = MAPSA(a)
firmver = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(firmver)



sdur = options.shutterdur

snum = options.number
sdel = 0xFFF
slen = 0xFFF
sdist = 0xFF



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
if options.calib == 'True':
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

cntsperspill = 0.
startrun=True


if options.norm == 'False':
	thdac = [options.thresh,options.thresh,options.thresh,options.thresh,options.thresh,options.thresh]
else:
	thdac = [options.thresh,90,options.thresh,90,options.thresh,90]



Endloop = False
spillnumber = 0

confdict = {'OM':[memmode]*6,'RT':[None]*6,'SCW':[0]*6,'SH2':[None]*6,'SH1':[None]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[None]*6,'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[None]*6,'ARR':[AR]*6,'CER':[CE]*6,'SP':[None]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}

if options.record=='True':

	timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
	foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr
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
	if options.setting == 'testbeam':
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



mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,CE)
if options.setting == 'manual':


	if options.autospill == 'True':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")
		sys.stdout = Outf1


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
		sys.stdout = Outf1
		print 
		print
		print "---------------------------------------------------------------------------"
		print "-----------------------------Starting spill " + str(spillnumber)+"------------------------------"
		print "---------------------------------------------------------------------------"
		print
		sys.stdout = saveout

		config = mapsa.config(Config=1,string='calibrated')
		config.upload()

		config.modifyfull(confdict)  

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
			mapsa.daq().Sequencer_init(0x0,sdur,mem=1)

			#print mem
			sys.stdout = saveout
			pix,mem = mapsa.daq().read_data(1)
			sys.stdout = Outf1
			parray = []
			marray = []
			cntspershutter = 0
			for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)

					parray.append(pix[i])

					sys.stdout = saveout
					marray.append(mpa[i].daq().read_memory(mem[i],memmode))

					sys.stdout = Outf1
					cntsperspill += sum(pix[i])
					cntspershutter += sum(pix[i])
			sys.stdout = saveout
			print "Total counts: " + str(cntsperspill)
			print "Counts this shutter: " +   str(cntspershutter)
			sys.stdout = Outf1
			if cntsperspill>100.:
				startrun=False
			if cntspershutter == 0 and options.skip=='True':
				sys.stdout = saveout
	
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

				ipix=0

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
			for tv in tree_vars.keys():
				sys.stdout = saveout
				for i in range(0,len(temp_vars[tv])):
					tree_vars[tv][i] = temp_vars[tv][i]
	
				sys.stdout = Outf1

			tree.Fill()

			print "---------------------------------------------------------------------------"
		

	    F.Write()
	    F.Close()
if options.setting == 'testbeam' or options.setting == 'default':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to start and Enter to quit"
		raw_input("...")
		sys.stdout = Outf1


		config = mapsa.config(Config=1,string='calibrated')
		config.upload()

		config.modifyfull(confdict)  



	
		if options.setting == 'testbeam':
			a._hw.getNode("Shutter").getNode("time").write(options.shutterdur)
			a._hw.dispatch()
			mapsa.daq().Testbeam_init(clock='glib',calib=0x0)
		if options.setting == 'default':
			mapsa.daq().Sequencer_init(0x1,sdur,mem=1)
			mapsa.daq().header_init()
		ibuffer=1
		
		iread=0
		cntsperspill = 0
		while True:
	  
			buffers_num = a._hw.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
			spill = a._hw.getNode("Control").getNode('Sequencer').getNode('spill').read()
			a._hw.dispatch()

			sys.stdout = saveout

			#print buffers_num
			if False:#buffers_num==4:
				offs = 0x40000000
				regs = [0x0,0x1,0x2,0x3,0x80,0x201,0x202,0x203,0x204,0x205]
				for r in regs:
					sys.stdout = saveout
					rval = offs+r
					print str(hex(rval))
					val = a._hw.getClient().read(int(rval))
					a._hw.dispatch()
					print binary(val)

			sys.stdout = Outf1
		
			if buffers_num<4:	
				shutters+=1
				iread+=1
				sys.stdout = saveout

				pix,mem = mapsa.daq().read_data(ibuffer,wait=False)

				#print buffers_num
				sys.stdout = Outf1
				if options.setting == 'testbeam':
					total_triggers,trigger_counter,Offset_BEAM,Offset_MPA = mapsa.daq().read_trig(ibuffer)


				sys.stdout = Outf1

				parray = []
				marray = []
				cntspershutter = 0
				for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)
					parray.append(pix[i])
					cntspershutter+=sum(pix[i])
					sys.stdout = saveout
					marray.append(mpa[i].daq().read_memory(mem[i],memmode))
					sys.stdout = Outf1
				cntsperspill+=cntspershutter
				sys.stdout = saveout
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)
				print "Reading buffer: " + str(ibuffer)
				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers Total: " + str(total_triggers)
				print 
				sys.stdout = Outf1
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)
				print "Reading buffer: " + str(ibuffer)
				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers Total: " + str(total_triggers)
				print 


				if options.setting == 'testbeam':
	
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
	
					ipix=0

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
				if options.setting == 'testbeam':
	
					temp_vars["TRIG_COUNTS_SHUTTER"] = [trigger_counter]
					temp_vars["TRIG_COUNTS_TOTAL"] = [total_triggers]
					temp_vars["TRIG_OFFSET_BEAM"] = offsetbeam
					temp_vars["TRIG_OFFSET_MPA"] = offsetmpa

				for tv in tree_vars.keys():
					sys.stdout = saveout

					for i in range(0,len(temp_vars[tv])):
						tree_vars[tv][i] = temp_vars[tv][i]
	
					sys.stdout = Outf1

				tree.Fill()
				ibuffer+=1
				if ibuffer >4:
					ibuffer=1 
				print "---------------------------------------------------------------------------"

     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
				for ibuffer in range(1,5):
					pix,mem = mapsa.daq().read_data(ibuffer,wait=False)
				a._hw.getNode("Control").getNode('testbeam_mode').write(0x0)
        			line = raw_input()
				print "Ending loop"
        			break

	        F.Write()
	        F.Close()

print ""
print "Done"
