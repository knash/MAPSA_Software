from MPA_config import *
from MPA_daq import *
from MPA_scurve import *
from MPA_testbeam import *
class MPA:
	def __init__(self, hw, nmpa):
		self._hw     		= 	hw
		self._nmpa     		= 	nmpa
 		self.xmlfile		=	'clear.xml'
	def daq(self):
		return MPA_daq(self._hw, self._nmpa )
	def config(self, xmlfile):
		self.xmlfile = xmlfile
		return MPA_config(self._hw, self._nmpa, xmlfile = self.xmlfile  )
	def scurve(self):
		return MPA_scurve(self._hw, self._nmpa ,  xmlfile = self.xmlfile)
	def testbeam(self):
		return MPA_testbeam(self._hw, self._nmpa )

