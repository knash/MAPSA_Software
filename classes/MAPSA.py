#Functions related to the MAPSA object - turning on voltages / getting a specific MPA 

from MPA import *
from MAPSA_daq import *
from MAPSA_config import *
class MAPSA:
	def __init__(self, uasic):
		self._dev    		= 	uasic
		self._hw     		= 	self._dev._hw
		self._Utility 		=  	self._hw.getNode("Utility")

	def getMPA(self, nmpa):
		return MPA( self._hw,nmpa)

	def daq(self):
		return MAPSA_daq( self._hw)

	def config(self,Config,string):
		return MAPSA_config( self._hw,Config,string)

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
			count = count + 1
			if count > 100:
				print "Idle"
				return 0
                return 1

	def VDDPST_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x1)
		self._hw.dispatch()
		#write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x1)
		#self._hw.dispatch()
		time.sleep(0.01)

		#return self._voltage_wait("VDDPST","on")


	def DVDD_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x1)
		self._hw.dispatch()
		#write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x1)
		#self._hw.dispatch()
		time.sleep(0.01)

		#return self._voltage_wait("DVDD","on")

	def AVDD_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x1)
		self._hw.dispatch()
		#write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x1)
		#self._hw.dispatch()
		time.sleep(0.01)
		#if self._voltage_wait("AVDD","on"):
		if True:
			write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x1)
			self._hw.dispatch()
			write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x1)
			self._hw.dispatch()
			print "VBIFEED on"
			write = self._Utility.getNode('DAC_register').write(0x12BE)
			self._hw.dispatch()
			time.sleep(0.01)
			print "VBIAS on"
			write = self._Utility.getNode('DAC_register').write(0x10BE)
			self._hw.dispatch()
			time.sleep(0.01)
			print "VBIPRE on"
			write = self._Utility.getNode('DAC_register').write(0x11BE)
			self._hw.dispatch()
			time.sleep(0.01)

			return 1
		else:
			return 0

	def PVDD_on(self):

		write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x1)
		self._hw.dispatch()
		#write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x1)
		#self._hw.dispatch()
		time.sleep(0.01)

		#return self._voltage_wait("PVDD","on")

	def VBIAS_on(self):
		write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x1)
		self._hw.dispatch()
		time.sleep(0.01)
		#return self._voltage_wait("VBIAS","on")






	def VDDPST_off(self):
	
		write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x0)
		self._hw.dispatch()
		write = self._Utility.getNode('MPA_settings').getNode("VDDPST_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.01)

		return self._voltage_wait("VDDPST","off")

	def DVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x0)
		self._hw.dispatch()
		write = self._Utility.getNode('MPA_settings').getNode("DVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.01)
		return self._voltage_wait("DVDD","off")

	def AVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x0)
		self._hw.dispatch()
		write = self._Utility.getNode('MPA_settings').getNode("AVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.01)
		if self._voltage_wait("AVDD","off"):
			print "VBIPRE off"
			write = self._Utility.getNode('DAC_register').write(0x1100)
			self._hw.dispatch()
			time.sleep(0.01)

			print "VBIAS off"
			write = self._Utility.getNode('DAC_register').write(0x1000)
			self._hw.dispatch()
			time.sleep(0.01)

			print "VBIFEED off"
			write = self._Utility.getNode('DAC_register').write(0x1200)
			self._hw.dispatch()
			time.sleep(0.01)
			return 1
		else:
			return 0
	def PVDD_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x0)
		self._hw.dispatch()
		write = self._Utility.getNode('MPA_settings').getNode("PVDD_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.01)
		return self._voltage_wait("PVDD","off")

	def VBIAS_off(self):
		write = self._Utility.getNode('MPA_settings').getNode("VBIAS_enable").write(0x0)
		self._hw.dispatch()
		time.sleep(0.01)
		return self._voltage_wait("VBIAS","off")


	def Safe_power_on(self):
		success=False
		print "VDDPST on"
		if mapsa.VDDPST_on():
			time.sleep(0.1)
			print "DVDD on"
			if mapsa.DVDD_on():
				time.sleep(0.1)
				print "AVDD on"
				if mapsa.AVDD_on():
					time.sleep(0.1)
					print "PVDD on"
					if mapsa.PVDD_on():
						print "Power on completed sucessfully"
						success=True
		if not success:
			print "Power on failed, powering off"
			mapsa.Safe_power_off()
			logging.error("Power on unsuccessful")
		return success

	def Safe_power_off(self):
		success=False
		print "PVDD off"
		if mapsa.PVDD_off() :
			time.sleep(0.1)
			print "AVDD off"
			if mapsa.AVDD_off():
				time.sleep(0.1)
				print "DVDD off"
				if mapsa.DVDD_off() :
					time.sleep(0.1)
					print "VDDPST off"
					if mapsa.VDDPST_off():
						print "Power on completed sucessfully"
						success=True
		if not success:
			logging.error("Power off unsuccessful")
		return success
