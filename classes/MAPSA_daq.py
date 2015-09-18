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

		self._puls_num   = self._Shutter.getNode("Strobe").getNode("number")
		self._puls_len   = self._Shutter.getNode("Strobe").getNode("length")
		self._puls_dist  = self._Shutter.getNode("Strobe").getNode("distance")
		self._puls_del   = self._Shutter.getNode("Strobe").getNode("delay")
		self._shuttertime	= self._Shutter.getNode("time")
		self._shutterbusy	= self._Shutter.getNode("busy")

		self._readoutbusy  = self._Control.getNode("Sequencer").getNode("busy")
		self._calib  = self._Control.getNode("Sequencer").getNode("calibration")
		self._read  = self._Control.getNode("Sequencer").getNode("readout")
		self._buffers  = self._Control.getNode("Sequencer").getNode("buffers_index")
		self._data_continuous  = self._Control.getNode("Sequencer").getNode("datataking_continuous")

		self._memory  = self._Readout.getNode("Memory")
		self._counter  = self._Readout.getNode("Counter")


	def _wait(self):
		ready=3
		i=0
		while ready!=0:
			busyshutter = self._shutterbusy.read()
			busyread = self._readoutbusy.read()
			self._hw.dispatch()

			if busyshutter and ready==3:
				ready[i-1]-=1
			if busyread and ready==2:	
				ready[i-1]-=1
			if not busyread and ready==1:
				ready[i-1]-=1

			time.sleep(0.001)
			i+=1
			if i>10:
				return 0
		
		print "DAQ took " + i*0.001 + " seconds"
		return 1

	def calibrationpulse(self, npulse=128, length=50, dist=50, inidelay = 50):

			
		self._puls_num.write(npulse)  
		self._puls_len.write(length)
		self._puls_dist.write(dist)
		self._puls_del.write(inidelay)
		self._hw.dispatch()
		
		time.sleep(0.001)
		
		
		self._calib.write(1)
		self._read.write(0)
		self._data_continuous.write(0)
		self._buffers.write(1)
		self._hw.dispatch()
		
		time.sleep(0.001)

	def triggerloop(self,shutterdelay):
		cycle = (1000.0/320.0)

		delay = int(round(shutterdelay/cycle))
		if float(delay) != shutterdelay/cycle :
			print "Using " +str(delay*cycle)+"ns instead of " + str(shutterdelay)
		if len(hex_to_binary(frmt(delay)))>32:
			print "Shutter delay time out of bounds"

		self._shuttertime.write(delay)
		self._hw.dispatch()
		
		time.sleep(0.001)
		
		
		self._calib.write(0)
		self._read.write(1)

		self._data_continuous.write(1)

		self._buffers.write(1)
		self._hw.dispatch()

		time.sleep(0.001)

	def read_data(self,buffer_num=1):
		counts = []  
		mems = []  
		for i in range(1,7):
			pix,mem = MPA(self._hw,i).daq().read_data(buffer_num)
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







			
			
