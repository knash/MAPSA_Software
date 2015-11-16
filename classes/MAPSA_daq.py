#Functions related to data aquisition at the MAPSA level - starting calibration and data taking 
#as well as loops of MPA_daq readout objects for ease of use 

from MPA import *
from MPA_daq import *
from MAPSA_functions import *
class MAPSA_daq:
	
	def __init__(self, hw):
		self._hw     = hw

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")
		self._Sequencer		=	self._Control.getNode("Sequencer") 

		self._puls_num   = self._Shutter.getNode("Strobe").getNode("number")
		self._puls_len   = self._Shutter.getNode("Strobe").getNode("length")
		self._puls_dist  = self._Shutter.getNode("Strobe").getNode("distance")
		self._puls_del   = self._Shutter.getNode("Strobe").getNode("delay")
		self._shuttertime	= self._Shutter.getNode("time")
		self._shutterbusy	= self._Shutter.getNode("busy")
		self._shuttermode	= self._Shutter.getNode("mode")

		self._sequencerbusy  = self._Sequencer.getNode("busy")
		self._calib  = self._Sequencer.getNode("calibration")
		self._read  = self._Sequencer.getNode("readout")
		self._buffers  = self._Sequencer.getNode("buffers_index")
		self._data_continuous  = self._Sequencer.getNode("datataking_continuous")

		self._memory  = self._Readout.getNode("Memory")
		self._counter  = self._Readout.getNode("Counter")
		self._busyread  = self._Readout.getNode("busy")
		self._readmode  = self._Readout.getNode("memory_readout")
		self._readbuff  = self._Readout.getNode("buffer_num")

    		self._clken = self._Control.getNode("MPA_clock_enable") 		  
    		self._testbeam = self._Control.getNode("testbeam_mode") 		
    		self._testbeamclock = self._Control.getNode("testbeam_clock") 		    

	def _waitreadout(self):
		busyread = self._busyread.read()
		self._hw.dispatch()
		count = 0
		while busyread:
			time.sleep(0.005)
			busy = self._busyread.read()
		        self._hw.dispatch()
			count = count + 1
			if count > 100:
				print "readout Idle"
				return 0
		#print "Finished"
		#print "Readout took " + str(count*0.005) + " seconds"
                return 1
				

	def _waitsequencer(self):
		i=0
		busyseq = self._sequencerbusy.read()
		self._hw.dispatch()
		while busyseq:
			busyseq = self._sequencerbusy.read()
			self._hw.dispatch()

			time.sleep(0.001)
			i+=1
			if i>100:
				print "timeout"
				return 0
		
		#print "Sequencer took " + str(i*0.001) + " seconds"
		return 1



	def _waitshutter(self):
		i=0
		busyshutter = self._shutterbusy.read()
		self._hw.dispatch()
		while busyshutter:
			busyshutter = self._shutterbusy.read()
			self._hw.dispatch()

			time.sleep(0.001)
			i+=1
			if i>100:
				print "timeout"
				return 0
		
		#print "DAQ took " + str(i*0.001) + " seconds"
		return 1


	def calibrationpulse(self, npulse=128, length=50, dist=50, inidelay = 50,sdur = 0 ):

			
		self._puls_num.write(npulse)  
		self._puls_len.write(length)
		self._puls_dist.write(dist)
		self._puls_del.write(inidelay)
		self._shuttertime.write(sdur)
		self._hw.dispatch()
		
		time.sleep(0.001)
		
		
		self._calib.write(1)
		self._read.write(0)
		self._data_continuous.write(0)
		self._buffers.write(1)
		self._hw.dispatch()
		
		time.sleep(0.001)


	def start_readout(self,buffer_num=1,mode=0x1):

		self._readbuff.write(buffer_num-1)
		self._readmode.write(mode)
		self._hw.dispatch()



	def read_data(self,buffer_num=1,tb=0):
		counts = []  
		mems = []  
		for i in range(1,7):
			pix = []
			mem = []
			pix,mem = MPA(self._hw,i).daq().read_data(buffer_num,tb)

			counts.append(pix) 
			mems.append(mem)
		return counts,mems

	def read_memory(self,mode,buffer_num=1):
		BXs = [] 
		datas = [] 
		counts = [] 

		for i in range(1,7):
			BX, data, count = MPA(self._hw,i).daq().read_memory(mode,buffer_num)
			BXs.append(BX) 
			datas.append(data) 
			counts.append(count) 

		return 	BXs,datas,counts



	def Strobe_settings(self,snum,sdel,slen,sdist,sdur = 0):

		self._puls_num.write(snum)
		self._puls_del.write(sdel)
		self._puls_len.write(slen)
		self._puls_dist.write(sdist)

		self._shuttertime.write(sdur)
		self._hw.dispatch()
		#time.sleep(0.001)
		

			
	def Shutter_open(self,smode,sdur):			

		self._shuttermode.write(smode)
		self._hw.dispatch()

		self._waitshutter()
