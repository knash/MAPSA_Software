#To be used for special testbeam functions -- need to wait for firmware updates

from MAPSA_functions import *
from MPA_config import *
from MPA_daq import *
from MPA_scurve import *
from MPA_testbeam import *
class MAPSA_testbeam:

	def __init__(self, hw, nmpa,conf):#, fit):
		self._hw     = hw
		self._nmpa     = nmpa

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")
		self._conf    = conf
		self._daq     = MPA_daq(self._hw, self._nmpa)

		self._shutter    = self._hw.getNode("Shutter")
		self._shuttertime	= self._shutter.getNode("time")

	







	
					
