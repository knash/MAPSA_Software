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

	def read_memory(self, mode):
		(count, mem) = self.read_data()
		memory = np.array(mem)
		BX = []
		hit = []
		row = []
		col = []
		data = []
		bend = []
		
		if (mode == 2):
			for x in range(0,96):
				if (memory[x][0:16] == '00000000'):
					break
				BX.append(int(memory[x][0:16],2))
				nrow = [int(memory[x][16:21],2), int(memory[x][23:28],2), int(memory[x][30:35],2), int(memory[x][37:42],2), int(memory[x][44:49],2), int(memory[x][51:56],2), int(memory[x][58:63],2), int(memory[x][65:70],2)]
				#nrow = filter(lambda a: a !=0, nrow)
				ncol = [int(memory[x][21:23],2), int(memory[x][28:30],2), int(memory[x][35:37],2), int(memory[x][42:44],2), int(memory[x][49:51],2), int(memory[x][56:58],2), int(memory[x][63:65],2), int(memory[x][70:72],2)] 
				ncol = filter(lambda a: a !=0, ncol)
				if (ncol != []):
					nrow = nrow[8-len(ncol):8]
					col.append(ncol)
					row.append(nrow)
			data = [row,col]
		
		if (mode == 0):
			for x in range(0,96):
				if (memory[x][0:16] == '00000000'):
					break
				BX.append(int(memory[x][4:20],2))
				nrow = [int(memory[x][20:26],2), int(memory[x][33:39],2), int(memory[x][46:52],2), int(memory[x][59:65],2)]
				nbend = [int(memory[x][26:31],2), int(memory[x][39:44],2), int(memory[x][52:57],2), int(memory[x][65:70],2)] 
				ncol = [int(memory[x][31:33],2), int(memory[x][44:46],2), int(memory[x][57:59],2), int(memory[x][70:72],2)] 
				ncol = filter(lambda a: a !=0, ncol)
				
				
				if (ncol != []):
					nrow = nrow[4-len(ncol):4]
					nbend = nbend[4-len(ncol):4]
					col.append(ncol)
					row.append(nrow)
					bend.append(nbend)
			data = [row, bend, col]
		
		if (mode == 3):
			for x in range(0,96):
				if (memory[x][0:8] == '00000000'):
					break
				BX.append(int(memory[x][8:24],2))
				hit.append(memory [x][24:72])			
			
			hit = filter(lambda a: a!=0, hit)
			data = hit		
		
		BX = filter(lambda a: a!=0, BX)		
		return BX, data, count	
			
			


####################CURRENTLY EDITING
	def generate_curve(self, confs, pix = range(0,48), Npulse = 1000, charge = 15, fname = './results/scurve.txt', plot = 1, verbose = 0):
		for conf in confs:
			for x in range(0,48): 
				regN = x/2+1
				lor  = x%2
				if x not in pix:
					if (lor == 0):
						conf.modifypixel(regN,'PML', 0)
						conf.modifypixel(regN,'ARL', 0)
						conf.modifypixel(regN,'CEL', 0)
						conf.modifypixel(regN,'SR',  0)
					if (lor == 1):
						conf.modifypixel(regN,'PMR', 0)
						conf.modifypixel(regN,'ARR', 0)
						conf.modifypixel(regN,'CER', 0)
						conf.modifypixel(regN,'SR',  0)
				else:
					if (lor == 0):
						conf.modifypixel(regN,'PML', 1)
						conf.modifypixel(regN,'ARL', 1)
						conf.modifypixel(regN,'CEL', 1)
						conf.modifypixel(regN,'SR',  0) 	
					if (lor == 1):
						conf.modifypixel(regN,'PMR', 1)
						conf.modifypixel(regN,'ARR', 1)
						conf.modifypixel(regN,'CER', 1)
						conf.modifypixel(regN,'SR',  0) 		

		
			conf.modifyperiphery('CALDAC', charge)
			conf.modifyperiphery('THDAC', 0)
			conf.upload(0)
			self._hw.dispatch()
			list_counter = []
			DAC = []
	
		for x in range(0,256):
			done = 0;
			while not done:	
				counter = []
				self._conf.modifyperiphery('THDAC', x)
				self._conf.upload(0)
				self._conf._spi_wait()
				time.sleep(0.001)
				#self._daq.load_header()
				#self._conf._spi_wait()
				#time.sleep(0.001)
				self._daq.calibrationpulse(Npulse, 100, 500,184)
				self._daq._wait()



				time.sleep(0.001)
				(counter, mem) = self._daq.read_data()	

				self._daq._wait()

				time.sleep(0.001)				
				if (verbose):
					print ' TH ' +  str(x) + ' ' + str(counter)
				err = 0


##############################Probably want to put this back in with real HW


				#for y in range(2,50):
				#	if counter[y] > 10000:
				#		err = 1
				#if counter[0] == 0:
				#	self._daq.calibrationpulse(10, 10,10,10)
				#	self._daq.read_data()

##############################\Probably want to put this back in with real HW


				if ((err ==0)): #& (counter[0] == 65528)):
				        done = 1
				        counter.pop(0)
				        counter.pop(0)
				        list_counter.append(counter)
					DAC.append(x)	
			#for y in pix:
		scurve = np.array(list_counter)

		return scurve



			
			
