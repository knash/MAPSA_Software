#To be used for special scurve functions


from MPA import *
from MPA_daq import *
from MAPSA_functions import *
class MAPSA_scurve:

	def __init__(self, hw, nmpa, xmlfile):
		self._hw     = hw
		self._nmpa     = nmpa

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")
		self.xmlfile		=	xmlfile
		self._conf		= 	MPA_config(self._hw, self._nmpa, self.xmlfile )
		#self._conf    = conf
		self._daq     = MPA_daq(self._hw, self._nmpa)
		self._mapsadaq     = MAPSA_daq(self._hw, self._nmpa)
		

	def generate_curve(self, pix = range(0,48), Npulse = 1000, charge = 15, fname = './results/scurve.txt', plot = 1, verbose = 0):

		for x in range(0,48): 
			regN = x/2+1
			lor  = x%2
			if x not in pix:
				if (lor == 0):
					self._conf.modifypixel(regN,'PML', 0)
					self._conf.modifypixel(regN,'ARL', 0)
					self._conf.modifypixel(regN,'CEL', 0)
					self._conf.modifypixel(regN,'SR',  0)
				if (lor == 1):
					self._conf.modifypixel(regN,'PMR', 0)
					self._conf.modifypixel(regN,'ARR', 0)
					self._conf.modifypixel(regN,'CER', 0)
					self._conf.modifypixel(regN,'SR',  0)
			else:
				if (lor == 0):
					self._conf.modifypixel(regN,'PML', 1)
					self._conf.modifypixel(regN,'ARL', 1)
					self._conf.modifypixel(regN,'CEL', 1)
					self._conf.modifypixel(regN,'SR',  0) 	
				if (lor == 1):
					self._conf.modifypixel(regN,'PMR', 1)
					self._conf.modifypixel(regN,'ARR', 1)
					self._conf.modifypixel(regN,'CER', 1)
					self._conf.modifypixel(regN,'SR',  0) 		

		
		self._conf.modifyperiphery('CALDAC', charge)
		self._conf.modifyperiphery('THDAC', 0)
		self._conf.upload(0)
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









	
					
