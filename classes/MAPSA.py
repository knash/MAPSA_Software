#Functions related to the MAPSA object - turning on voltages / getting a specific MPA 

from MPA import *
from MAPSA_daq import *
class MAPSA:
	def __init__(self, uasic):
		self._dev    		= 	uasic
		self._hw     		= 	self._dev._hw
		self._Utility 		=  	self._hw.getNode("Utility")

	def getMPA(self, nmpa):
		return MPA( self._hw,nmpa)

	def daq(self):
		return MAPSA_daq( self._hw)

	def _voltage_wait(self,supply,state):

		if state=="on":
			X=0	
		elif state=="off":
			X=1
		else:
			"wrong state"
			return 0					

		read = self._Utility.getNode('MPA_settings_read').getNode(supply+"_enable").read()
		self._hw.dispatch()
		count = 0
		while read == X:
			time.sleep(0.005)
			read = self._Utility.getNode('MPA_settings_read').getNode(supply+"_enable").read()
			self._hw.dispatch()
			print read
			count = count + 1
			if count > 100:
				print "Idle"
				return 0
                return 1

	def VDDPST_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("VDDPST","on")

	def DVDD_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("DVDD","on")

	def AVDD_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("AVDD","on")

	def PVDD_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("PVDD","on")

	def VBIAS_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("VBIAS","on")






	def VDDPST_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("VDDPST","off")

	def DVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("DVDD","off")

	def AVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("AVDD","off")

	def PVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("PVDD","off")

	def VBIAS_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.001)
		return self._voltage_wait("VBIAS","off")

