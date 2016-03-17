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


parser.add_option('-T', '--testclock', metavar='F', type='string', action='store',
default	=	'glib',
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
default	=	'True',
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

parser.add_option('-D', '--direction', metavar='F', type='string', action='store',
default	=	'glib',
dest	=	'direction',
help	=	'strip direction (glib or mpa)')

parser.add_option('-L', '--loops', metavar='F', type='int', action='store',
default	=	-1,
dest	=	'loops',
help	=	'number of daq loops')


parser.add_option('-p', '--phase', metavar='F', type='int', action='store',
default	=	0,
dest	=	'phase',
help	=	'beam phase offset')




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

#a._hw.getNode("Control").getNode("logic_reset").write(0x1)
#a._hw.dispatch()
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
Startspill=True


if options.norm == 'False':
	thdac = [options.thresh,options.thresh,options.thresh,options.thresh,options.thresh,options.thresh]
else:
	thdac = [options.thresh,90,options.thresh,90,options.thresh,90]



Endloop = False
spillnumber = 0

confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
vararr = []

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
	tree_vars["SPILL"] = array('L',[0])
	#tree_vars["TIMESTAMP"] = array('L',[0])
	if options.setting == 'testbeam':
		tree_vars["TRIG_COUNTS_SHUTTER"] = array('L',[0])
		tree_vars["TRIG_COUNTS_TOTAL_SHUTTER"] = array('L',[0])
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

Kill=False

mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,CE)
if options.setting == 'manual':

	bufferdata=[]
	if options.autospill == 'True':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to quit"
		#raw_input("...")
		sys.stdout = Outf1


	while Endloop == False:
	    Endspill = False
	    Startspill=True
	    while Endspill == False:
		zeroshutters=0
		cntsperspill = 0
		Startspill=True
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
			pix,mem = mapsa.daq().read_data(1,True,True)
			sys.stdout = Outf1
			parray = []
			marray = []
			cntspershutter = 0
			for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)

					parray.append(pix[i])

					sys.stdout = saveout
					#marray.append(mpa[i].daq().read_memory(mem[i],memmode))
					marray.append(mem[i])
					sys.stdout = Outf1
					cntsperspill += sum(pix[i])
					cntspershutter += sum(pix[i])
			sys.stdout = saveout
			print "Total counts: " + str(cntsperspill)
			print "Counts this shutter: " +   str(cntspershutter)
			sys.stdout = Outf1
			if cntsperspill>100.:
				Startspill=False
			if cntspershutter == 0 and options.skip=='True':
				
	
				sys.stdout = Outf1

				if Startspill==False:
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
			
						temp_vars["SR_UN_MPA_"+str(i)]=memo

						sys.stdout = Outf1
						i+=1

					bufferdata=memo[0]



			temp_vars["SPILL"] = [spillnumber]
			vararr.append(temp_vars)
			#for tv in tree_vars.keys():
			#	sys.stdout = saveout
			#	for i in range(0,len(temp_vars[tv])):
			#		tree_vars[tv][i] = temp_vars[tv][i]
	
			#	sys.stdout = Outf1

			#tree.Fill()

			print "---------------------------------------------------------------------------"
	    sys.stdout = saveout
	    print "Writing events to tree..."



	    nev = 0
	    for ev in vararr:
		nev+=1
		print nev
		for impa in range(0,len(mpa)):
			
			mem[impa] = mpa[impa].daq().formatmem(ev["SR_UN_MPA_"+str(impa)])
			memo = mpa[impa].daq().read_memory(mem[impa],memmode)



			for p in range(0,96):
				if p>len(memo[0]):
					memo[0].append(int(0))
					memo[1].append('0')

				BXmemo = np.array(memo[0])	
				DATAmemo = np.array(memo[1])

				DATAmemoint = []	
				for DATAmem in DATAmemo:
					DATAmemoint.append(long(DATAmem,2)) 
			

			ev["SR_BX_MPA_"+str(impa)] = BXmemo
			ev["SR_MPA_"+str(impa)] = DATAmemoint





		for tv in tree_vars.keys():
			if 'SR_UN_MPA' in tv:
				continue 
			for i in range(0,len(ev[tv])):
				tree_vars[tv][i] = ev[tv][i]
			tree.Fill()
	    F.Write()
	    F.Close()

if options.setting == 'strip':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to quit"
		#raw_input("...")
		confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[0,0,0,0,0,0],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[0,0,0,0,0,0],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}

		config = mapsa.config(Config=1,string='calibrated')
		config.upload()
		config.modifyfull(confdict)  
		config.upload()
		a._hw.dispatch()
		confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1,0,0,0,0,0],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[0,0,0,0,0,0],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
		config.modifyfull(confdict,pixels=[5,6])  
		config.upload()
		a._hw.dispatch()
 		#config.modifypixel( 5,['PML'],[1]*6)
 		#config._confs[0].upload()
		#config.upload()
		a._hw.dispatch()
		mapsa.daq().header_init()

		

		iread=0
		cntsperspill = 0
		mpasettings = a._hw.getNode("Utility").getNode("MPA_settings").read()
		mpasettingsread = a._hw.getNode("Utility").getNode("MPA_settings_read").read()
		#a._hw.getNode("Control").getNode("strip_phase").write(0)
		#a._hw.getNode("Utility").getNode("MPA_settings").getNode('strip_direction').write(0)
		a._hw.dispatch()

		#if options.direction=='glib':
		#	print "writing glib"
		#	a._hw.getNode("Strip").getNode("enable_TEMP").write(0x00)
		#	a._hw.dispatch()
		#if options.direction=='mpa':
		#	print "writing mpa"
		a._hw.getNode("Strip").getNode("enable").write(0x3F)
		a._hw.dispatch()

		read1 = a._hw.getNode("Strip").getNode("enable").read()
		a._hw.dispatch()
		numloops=0

		while True:
			if options.loops!=-1:
				if numloops>=options.loops:
					Kill=True
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or Kill:
        			line = raw_input()
				print "Ending loop"
	    			Endspill = True
	    			Endloop = True
        			break







			confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[0,0,0,0,0,0],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[0,0,0,0,0,0],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
			config.modifyfull(confdict)  
			config.upload()
			a._hw.dispatch()
			confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1,0,0,0,0,0],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[0,0,0,0,0,0],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
			
			config.modifyfull(confdict,pixels=[numloops,numloops+1])  
			config.upload()
			a._hw.dispatch()


			stripread = a._hw.getNode("Strip").getNode("enable").read()
			print "new event"
			a._hw.getNode("Control").getNode("full_flag").write(0x1)
			a._hw.dispatch()
			mpasettings = a._hw.getNode("Utility").getNode("MPA_settings").read()

			mpasettingsread = a._hw.getNode("Utility").getNode("MPA_settings_read").read()
			a._hw.dispatch()
			#print "MPA settings"
			#print binary(mpasettings)
			#print "MPA settings read"
			#print binary(mpasettingsread)
			#print "strip enable register"
			#print binary(stripread)
			#print "Current Configuration:"
			#print confdict
			#print 
			

			mapsa.daq().Sequencer_init(0x0,sdur,mem=1)
			pix,mem = mapsa.daq().read_data(1)
			print 'reading counts'
			parray = []
			marray = []
			"""for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)

					parray.append(pix[i])

					#marray.append(mpa[i].daq().read_memory(mem[i],memmode))

					print pix[i]"""


			for i in range(0,1):
					pix[i].pop(0)
					pix[i].pop(0)

					#marray.append(mpa[i].daq().read_memory(mem[i],memmode))
					rows = [0]*16,[0]*16,[0]*16
					for ipixel in range(0,len(pix[i])):
						if 0<ipixel<16:
							rows[0][ipixel]= pix[i][ipixel]
						if 16<ipixel<31:
							rows[1][31-ipixel]= pix[i][ipixel]
						if 31<ipixel<46:
							rows[2][-31+ipixel]= pix[i][ipixel]
					for r in rows:
						print str(r).replace('[','').replace(']','').replace(',','')

			#print mem[1]
			write1 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA1").read()
			write2 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA2").read()
			write3 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA3").read()
			write4 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA4").read()
			write5 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA5").read()
			write6 = a._hw.getNode("Strip").getNode("write_address").getNode("MPA6").read()

			strip1 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA1").readBlock(0x400)
			strip2 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA2").readBlock(0x400)
			strip3 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA3").readBlock(0x400)
			strip4 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA4").readBlock(0x400)
			strip5 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA5").readBlock(0x400)
			strip6 = a._hw.getNode("Strip").getNode("buffer_in").getNode("MPA6").readBlock(0x400)

			out1 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA1").read()
			out2 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA2").read()
			out3 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA3").read()
			out4 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA4").read()
			out5 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA5").read()
			out6 = a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA6").read()

		        a._hw.dispatch()
			stripf = []
			print "counts"
			for strip in [strip1,strip2,strip3,strip4,strip5,strip6]:
				temparr = []
				for iel in range(0,len(strip)):
					temparr.append(binary(strip[iel])[-16:])	
				stripf.append(temparr)
					

			print 
			#print "MPA1"
			#print "strip write address"
			#print hex(write1)
			#print "number of strip words"
			#print write1>>2
			print "strips"
			#print stripf[0][1]
			#print 
			for strip in stripf[0]:
				if strip!='0000000000000000':
					print strip
					break
			#print stripf[0][0]
			#print stripf[0][1]
		#	print "out buffer"
		#	print out1
			print 
			"""print "MPA2"
			print "strip write address"
			print hex(write2)
			#print "strip words"
			#print write2>>2
			print "strip words"
			for strip in stripf[1]:
				if strip!='0000000000000000':
					print strip
			print "out buffer"
			print out2
			print 
			print "MPA3"
			print "strip write address"
			print hex(write3)
			print "strip words"
			for strip in stripf[2]:
				if strip!='0000000000000000':
					print strip
			print "out buffer"
			print out3
			print 
			print "MPA4"
			print "strip write address"
			print hex(write4)
			print "strip words"
			for strip in stripf[3]:
				if strip!='0000000000000000':
					print strip
			print "out buffer"
			print out4
			print 
			print "MPA5"
			print "strip write address"
			print hex(write5)
			print "strip words"
			for strip in stripf[4]:
				if strip!='0000000000000000':
					print strip
			print "out buffer"
			print out5
			print 
			print "MPA6"
			print "strip write address"
			print hex(write6)
			print "strip words"
			for strip in stripf[5]:
				if strip!='0000000000000000':
					print strip
			print "out buffer"
			print out6
			print 
			print "-------------------------------"
			print """
			numloops+=1




if options.setting == 'stripinput':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to quit"
		#raw_input("...")
		confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1,1,1,1,1,1],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1,1,1,1,1,1],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
		breakout=False
		config = mapsa.config(Config=1,string='calibrated')
		config.upload()
		config.modifyfull(confdict)  
		config.upload()
		a._hw.dispatch()
 		#config.modifypixel( 5,['PML'],[1]*6)
 		#config._confs[0].upload()
		#config.upload()
		#a._hw.dispatch()
		mapsa.daq().header_init()

		

		iread=0
		cntsperspill = 0
		#mpasettingsread = a._hw.getNode("Utility").getNode("MPA_settings_read").read()
		#a._hw.getNode("Control").getNode("strip_phase").write(0)
		a._hw.getNode("Utility").getNode("MPA_settings").getNode('strip_direction').write(0x3F)
		a._hw.dispatch()

		a._hw.getNode("Strip").getNode("enable").write(0x0)
		a._hw.dispatch()

		sphase = 0
		numloops=0
		while True:
			#print sphase
			sphase+=1
			if sphase>375:
				sphase=0
    			a._hw.getNode("Control").getNode("strip_phase").write(sphase)
			a._hw.dispatch()
			print sphase
			if options.loops!=-1:
				if numloops>=options.loops:
					Kill=True
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or Kill:
        			line = raw_input()
				print "Ending loop"
	    			Endspill = True
	    			Endloop = True
        			break







			#confdict = {'OM':[memmode]*6,'RT':[1]*6,'SCW':[1]*6,'SH2':[2]*6,'SH1':[2]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[0,0,0,0,0,0],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[2]*6,'PMR':[0,0,0,0,0,0],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
			#config.modifyfull(confdict)  
			#config.upload()
			#a._hw.dispatch()
			#confdict = {'OM':[memmode]*6,'RT':[1]*6,'SCW':[1]*6,'SH2':[2]*6,'SH1':[2]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1,1,1,1,1,1],'ARL':[AR]*6,'CEL':[CE]*6,'CW':[2]*6,'PMR':[1,1,1,1,1,1],'ARR':[AR]*6,'CER':[CE]*6,'SP':[0]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
			
			#config.modifyfull(confdict,pixels=[numloops,numloops+1])  
			#config.upload()
			#a._hw.dispatch()


			print "new event"
			#a._hw.getNode("Control").getNode("full_flag").write(0x1)
			#a._hw.dispatch()
			#mpasettings = a._hw.getNode("Utility").getNode("MPA_settings").read()
			#mpasettingsread = a._hw.getNode("Utility").getNode("MPA_settings_read").read()
			#a._hw.dispatch()
			#print "MPA settings"
			#print binary(mpasettings)
			#print "MPA settings read"
			#print binary(mpasettingsread)
			#print "strip enable register"
			#print binary(stripread)
			#print "Current Configuration:"
			#print confdict
			#print 
		
			a._hw.getNode("Utility").getNode("MPA_settings").getNode('strip_direction').write(0x3F)
			a._hw.dispatch()

			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA1").write(0x810)
			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA2").write(0x810)
			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA3").write(0x810)
			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA4").write(0x810)
			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA5").write(0x810)
			a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA6").write(0x810)
		        a._hw.dispatch()
			a._hw.getNode("Strip").getNode("write").write(0x3F)
			a._hw.dispatch()
			mapsa.daq().Sequencer_init(0x0,sdur,mem=1)
			pix,mem = mapsa.daq().read_data(1)
			print 'reading counts'
			parray = []
			marray = []
			#print mem
			for i in range(0,6):
					pix[i].pop(0)
					pix[i].pop(0)

					parray.append(pix[i])

					marray.append(mpa[i].daq().read_memory(mem[i],memmode))

			print marray

			for i in range(0,6):

					#pix[i].pop(0)
					#pix[i].pop(0)

					#marray.append(mpa[i].daq().read_memory(mem[i],memmode))
					rows = [0]*16,[0]*16,[0]*16
					for ipixel in range(0,len(pix[i])):

						if 0<=ipixel<16:
							rows[0][ipixel]= pix[i][ipixel]
						if 16<=ipixel<32:
							rows[1][31-ipixel]= pix[i][ipixel]
						if 32<=ipixel<48:
							rows[2][-32+ipixel]= pix[i][ipixel]
					for r in rows:
						print str(r).replace('[','').replace(']','').replace(',','')
			for me in mem:
				print me[0]
				for m in me:
					if m!='000000000000000000000000000000000000000000000000000000000000000000000000' and m!='00000000000000000000000000000000000000000000000000000000000000000000000':
						print m
						breakout=True

			if breakout:
				break
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA1").write(0xFFFF)
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA2").write(0xFFFF)
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA3").write(0xFFFF)
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA4").write(0xFFFF)
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA5").write(0xFFFF)
			#a._hw.getNode("Strip").getNode("buffer_out").getNode("MPA6").write(0xFFFF)


			stripf = []


			print 
			
			numloops+=1



if options.setting == 'testbeam' or options.setting == 'default':
		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to quit"
		#raw_input("...")
		sys.stdout = Outf1


		config = mapsa.config(Config=1,string='calibrated')
		config.upload()

		config.modifyfull(confdict)  



	
		if options.setting == 'testbeam':
			polltime = 5000
			a._hw.getNode("Shutter").getNode("time").write(options.shutterdur)
			a._hw.dispatch()
			mapsa.daq().Testbeam_init(clock=options.testclock ,calib=0x0)
			mapsa.daq().header_init()
		if options.setting == 'default':
			polltime = 200
			mapsa.daq().Sequencer_init(0x1,sdur,mem=1)
			mapsa.daq().header_init()



		time.sleep(0.1)
		for cbuff in range(1,5):
			cpix,cmem = mapsa.daq().read_data(cbuff,wait=False)
			if options.setting == 'testbeam':
				ctotal_triggers,ctrigger_counter,ctrigger_total_counter,cOffset_BEAM,cOffset_MPA = mapsa.daq().read_trig(cbuff)
		time.sleep(0.1)


		ibuffer=1
		
		iread=0



	        Endrun = False

		zeroshutters = 0
		numloops=0

	  	poll =  0
		a._hw.getNode("Control").getNode("shutter_delay").write(options.phase)
		a._hw.dispatch()
		a._hw.getNode("Control").getNode("beam_on").write(0x1)
		a._hw.dispatch()

		while Endrun == False:
		    Endspill = False
		    Startspill=True
		    cntsperspill = 0
		    spillnumber+=1
		    sys.stdout = saveout
		    print "Starting spill " + str(spillnumber)
		    start = time.time()
		    sys.stdout = Outf1
		    print 
		    print
		    print "---------------------------------------------------------------------------"
		    print "-----------------------------Starting spill " + str(spillnumber)+"------------------------------"
		    print "---------------------------------------------------------------------------"
		    print
		    sys.stdout = saveout
		    while Endspill == False:


	

			buffers_num = a._hw.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
			spill = a._hw.getNode("Control").getNode('Sequencer').getNode('spill').read()
			buffers_index = a._hw.getNode("Control").getNode('Sequencer').getNode("buffers_index").read()
			a._hw.dispatch()
			sys.stdout = saveout
			#print buffers_num
			if options.loops!=-1:
				if numloops>=options.loops:
					Kill=True
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or Kill:
				 
				for ibuffer in range(1,5):
					pix,mem = mapsa.daq().read_data(ibuffer,wait=False)
				a._hw.getNode("Control").getNode('testbeam_mode').write(0x0)
        			line = raw_input()
				print "Ending loop"
				Endrun = True
				Endspill = True
        			break

	  		poll += 1


			if poll % polltime == 0:
		    		sys.stdout = saveout
				cur = time.time()
				if Startspill==True:
					print "Waiting for spill for " +str(cur-start)+ " seconds"
				if Startspill==False:
					if cur-start>3.:
						print "Spill ended"
						Endspill == True
						if options.setting == 'testbeam':
							Endrun = True
						break
					else:
						print "Idle for " +str(cur-start)+ " seconds"
			#if True:
			if buffers_num<4:	
				shutters+=1
				iread+=1
				sys.stdout = saveout
				#print 	"Buffer index pre trig " + str(buffers_index)

				#time.sleep(0.001)
				if options.setting == 'testbeam':
					total_triggers,trigger_counter,trigger_total_counter,Offset_BEAM,Offset_MPA = mapsa.daq().read_trig(ibuffer)

				pix,mem = mapsa.daq().read_data(ibuffer,wait=False,Fast=True)
				#print buffers_num


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
					#marray.append(mpa[i].daq().read_memory(mem[i],memmode))
					marray.append(mem[i])
					sys.stdout = Outf1

				if cntspershutter != 0 or options.setting == 'testbeam':
					print "Reading buffer: " + str(ibuffer)
					sys.stdout = saveout
					print "Reading buffer: " + str(ibuffer)
					sys.stdout = Outf1
				ibuffer+=1
				if ibuffer >4:
					ibuffer=1 


				if cntsperspill>60.:
					Startspill=False

				if cntspershutter == 0 and options.skip=='True' and options.setting != 'testbeam':
					continue



				if options.setting == 'testbeam':

					offdat = []
					#To fix
					offsetbeam = [0]*2048
					offsetmpa = [0]*2048
					sys.stdout = saveout

					for i in range(0,trigger_counter):
							
						offsetbeam[i] = Offset_BEAM[i]
						offdat.append(1000*(Offset_BEAM[i]-Offset_BEAM[0])/26.5)
						offsetmpa[i] = Offset_MPA[i]



					sys.stdout = Outf1
					print "Offset beam: " + str(offsetbeam)
					print "Offset mpa: " + str(offsetmpa)
					a._hw.dispatch()
					offset = []



				cntsperspill+=cntspershutter
				sys.stdout = saveout
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)

				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers at Shutter Start: " + str(trigger_total_counter)
					print "Triggers Total: " + str(total_triggers)
					print "Triggers Total: " + str(hex(total_triggers))
				print 
				sys.stdout = Outf1
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)

				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers at Shutter Start: " + str(trigger_total_counter)
					print "Triggers Total: " + str(total_triggers)
				print 





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
					allbx = []
					for memo in marray:
						temp_vars["SR_UN_MPA_"+str(i)]=memo				

						i+=1

				



				if options.setting == 'testbeam':
	
					temp_vars["TRIG_COUNTS_SHUTTER"] = [trigger_counter]
					temp_vars["TRIG_COUNTS_TOTAL_SHUTTER"] = [trigger_total_counter]
					temp_vars["TRIG_COUNTS_TOTAL"] = [total_triggers]
					temp_vars["TRIG_OFFSET_BEAM"] = offsetbeam
					temp_vars["TRIG_OFFSET_MPA"] = offsetmpa
				temp_vars["SPILL"] = [spillnumber]
				vararr.append(temp_vars)

				#for tv in tree_vars.keys():
				#	sys.stdout = saveout

				#	for i in range(0,len(temp_vars[tv])):
				#		tree_vars[tv][i] = temp_vars[tv][i]
	
				#	sys.stdout = Outf1

				#tree.Fill()
	
				print "---------------------------------------------------------------------------"
				numloops+=1
	  			poll = 0
				#start = time.time()
	    	print "Writing events to tree..."

	    	nev = 0
	    	for ev in vararr:
			nev+=1
			if nev%20==0:

				print nev
			for impa in range(0,len(mpa)):
				
				#print ev["SR_UN_MPA_"+str(impa)]
				#print len(ev["SR_UN_MPA_"+str(impa)])
				mem[impa] = mpa[impa].daq().formatmem(ev["SR_UN_MPA_"+str(impa)])

				memo = mpa[impa].daq().read_memory(mem[impa],memmode)



				for p in range(0,96):

					if p>len(memo[0]):
						memo[0].append(int(0))
						memo[1].append('0')

				BXmemo = np.array(memo[0])	
				DATAmemo = np.array(memo[1])

				DATAmemoint = []	
				for DATAmem in DATAmemo:
					DATAmemoint.append(long(DATAmem,2)) 
	
				ev["SR_BX_MPA_"+str(impa)] = BXmemo
				ev["SR_MPA_"+str(impa)] = DATAmemoint





			for tv in tree_vars.keys():
				if 'SR_UN_MPA' in tv:
					continue 
				for i in range(0,len(ev[tv])):
					tree_vars[tv][i] = ev[tv][i]
				tree.Fill()

		a._hw.getNode("Control").getNode("beam_on").write(0x0)
		a._hw.dispatch()

	        F.Write()
	        F.Close()

print ""
print "Done"
