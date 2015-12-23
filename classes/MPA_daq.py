#Functions related to data aquisition at the MPA level

from MAPSA_functions import *
class MPA_daq:
	
	def __init__(self, hw, nmpa):
		self._hw     = hw
		self._nmpa     = nmpa

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")


		self._puls_num   = self._Shutter.getNode("Strobe").getNode("number")
		self._puls_len   = self._Shutter.getNode("Strobe").getNode("length")
		self._puls_dist  = self._Shutter.getNode("Strobe").getNode("distance")
		self._puls_del   = self._Shutter.getNode("Strobe").getNode("delay")
		self._shuttertime	= self._Shutter.getNode("time")

		self._sequencerbusy  = self._Control.getNode("Sequencer").getNode("busy")
		self._calib  = self._Control.getNode("calibration")
		self._read  = self._Control.getNode("readout")

		self._buffers  = self._Control.getNode("Sequencer").getNode("buffers_index")
		self._data_continuous  = self._Control.getNode("Sequencer").getNode("datataking_continuous")



		self._memory  = self._Readout.getNode("Memory")
		self._counter  = self._Readout.getNode("Counter")
		self._readmode  = self._Control.getNode("readout")
		#self._readbuff  = self._Readout.getNode("buffer_num")


	

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
		
		return 1

	def read_raw(self,buffer_num,dcindex,wait=True):
		if wait==True:
			self._waitsequencer()
		counter_data  = self._counter.getNode("MPA"+str(dcindex)).getNode("buffer_"+str(buffer_num)).readBlock(25)
		memory_data = self._memory.getNode("MPA"+str(self._nmpa)).getNode("buffer_"+str(buffer_num)).readBlock(216)
		self._hw.dispatch()



		return [memory_data,counter_data]

	def read_data(self,buffer_num,dcindex=-1,wait=True):
		self._Readout.getNode("Header").getNode("MPA"+str(self._nmpa)).write(0xFFFFFFF0+self._nmpa)
		self._hw.dispatch()
		if dcindex==-1:
			dcindex=self._nmpa
		eshift = 0


		(memory_data,counter_data)= self.read_raw(buffer_num,dcindex,wait)

			
		pix,mem	= MPA_daq.format(counter_data,memory_data)
		return pix,mem	


	def format(self,counter_data,memory_data):


		pix = [None]*50
		mem = [None]*96
		for x in range(0,25):
				
			shift1 = int(0)
			shift2 = int(16)
	
	
			pix[2*x]  = int((counter_data[x] >> shift1) & 0xffff)
			pix[2*x+1]= int((counter_data[x] >> shift2) & 0xffff)


		memory_string = ''

		for x in range(0,216):
			memory_string = memory_string + str(binary(memory_data[215 - x]))
		
		for x in range(0,96):
			mem[x] = memory_string [x*72+1 : x*72+72+1]			
		return pix,mem	



	def read_memory(self, mem,mode):

		memory = np.array(mem)
		BX = []
		hit = []
		row = []
		col = []
		data = []
		bend = []
		

		if (mode == 1):
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
				#print memory[x]
		#		print memory[x][0:8]
		#		print memory[x][8:24]
		#		print memory[x][24:72]
		#		print 
		#		print 
				BX.append(int(memory[x][8:24],2))
				hit.append(memory [x][24:72])		
		
			
			#print hit
			hit = filter(lambda a: a!=0, hit)
			data = hit	
			#print data	
			

			#print 
		BX = filter(lambda a: a!=0, BX)		
		return BX, data	
			
	
	


	
			
			
