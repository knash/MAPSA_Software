#Functions related to data aquisition at the MAPSA level - starting calibration and data taking 
#as well as loops of MPA_daq readout objects for ease of use 



from MPA import *
from MPA_daq import *
from MAPSA_functions import *


class MAPSA_config:
	
	def __init__(self, hw,Config=1,string='default'):

		self._hw     		= 	hw
		self._Config		=	Config
		self._String		=	string
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


		self._Utility =  self._hw.getNode("Utility")
		self._Conf_busy    = self._Configuration.getNode("busy")

		self._Memory_DataConf   = self._Configuration.getNode("Memory_DataConf")

		self._confs = []
		self._confsxmlroot= []
		self._confsxmltree= []
		mpa = []  
		for i in range(1,7):
			mpa.append(MPA( self._hw,i))
			self._confs.append(mpa[i-1].config(xmlfile="data/Conf_"+self._String+"_MPA"+str(i)+"_config"+str(self._Config)+".xml"))
			self._confsxmltree.append(self._confs[i-1].xmltree)
			self._confsxmlroot.append(self._confs[i-1].xmlroot)

	def _spi_wait(self):
		busy = self._Conf_busy.read()
		self._hw.dispatch()
		while busy:
			time.sleep(0.001)
			busy = self._Conf_busy.read()
			self._hw.dispatch()
			#print busy

	def upload(self,show = 0):
		for conf in self._confs:
			conf.upload(show=0,Config=self._Config)


	def modifyperiphery(self,what, value):

		impa=0
		for conf in self._confs:
			conf.modifyperiphery(what, value[impa])
			conf.upload(show=0,Config=self._Config)
			impa+=1

	def modifypixel(self,which, what, value):

		impa=0
		for conf in self._confs:
			conf.modifypixel(which, what, value[impa])
			conf.upload(show=0,Config=self._Config)

			impa+=1





	def modifyfull(self, whichs):
				



		for key in whichs.keys():
			if whichs[key] == [None]*6:
				continue
			if any(['OM' in key,'RT' in key,'SCW' in key,'SH2' in key,'SH1' in key,'THDAC' in key,'CALDAC' in key]):
				self.modifyperiphery(key,whichs[key])
			elif any(['PML' in key,'ARL' in key,'CEL' in key,'CW' in key,'PMR' in key,'ARR' in key,'CER' in key,'SP' in key,'SR' in key,'TRIMDACL' in key,'TRIMDACR' in key]):
	
				for x in range(1,25):
					self.modifypixel(x,key,whichs[key])
	
		self.write()








	def write(self):
  
		self._spi_wait()
		self._hw.getNode("Configuration").getNode("num_MPA").write(0x6)
		self._hw.dispatch()
		self._spi_wait()
		self._hw.getNode("Configuration").getNode("mode").write(0x5)
		self._hw.dispatch()
		self._spi_wait()

    

