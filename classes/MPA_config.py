
from MAPSA_functions import *
class MPA_config:
	def __init__(self, hw, nmpa, xmlfile ):
		self._hw     = hw
		self._nmpa     = nmpa

		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration")
		self._Readout 		=  	self._hw.getNode("Readout")


		self._Control =  self._hw.getNode("Control")
		self._Utility =  self._hw.getNode("Utility")
		self._Configuration =  self._hw.getNode("Configuration")
		self._Conf_busy    = self._Configuration.getNode("busy")

		self._Memory_DataConf   = self._Configuration.getNode("Memory_DataConf")	

		self.xmlfile = xmlfile
		self.xmltree = ET.parse(self.xmlfile)
		self.xmlroot = self.xmltree.getroot()


	def _spi_wait(self):
		busy = self._Conf_busy.read()
		self._hw.dispatch()
		while busy:
			time.sleep(0.001)
			busy = self._Conf_busy.read()
			self._hw.dispatch()
			print busy

	def _get_pixel_fromfile(self, pixel):
		val = 0
		if ((int(pixel.attrib['n']))<17 and (int(pixel.attrib['n'])>8)):
			val = (  ((int(pixel.find('PMR').text) 	      & 1)	<< 0 )
				 | ((int(pixel.find('ARR').text) 	      & 1)	<< 1 )
				 | ((int(pixel.find('TRIMDACL').text)	& 31)	<< 2 ) 
				 | ((int(pixel.find('CER').text) 	      & 1)	<< 7 ) 
				 | ((int(pixel.find('SP').text) 	      & 1)	<< 8 )
				 | ((int(pixel.find('SR').text) 	      & 1)	<< 9 ) 
				 | ((int(pixel.find('PML').text) 	      & 1)	<< 10) 
				 | ((int(pixel.find('ARL').text) 	      & 1)	<< 11) 
				 | ((int(pixel.find('TRIMDACR').text)	& 31)	<< 12) 
				 | ((int(pixel.find('CEL').text) 	      & 1)	<< 17) 
				 | ((int(pixel.find('CW').text) 	      & 2)	<< 18))
				 
		elif ((int(pixel.attrib['n']))<25 and (int(pixel.attrib['n'])>0)):
			val = (  ((int(pixel.find('PML').text) 	      & 1)	<< 0 )
				 | ((int(pixel.find('ARL').text) 	      & 1)	<< 1 )
				 | ((int(pixel.find('TRIMDACL').text)	& 31)	<< 2 ) 
				 | ((int(pixel.find('CEL').text) 	      & 1)	<< 7 )
				 | ((int(pixel.find('CW').text) 	      & 3)	<< 8 )  
				 | ((int(pixel.find('PMR').text) 	      & 1)	<< 10) 
				 | ((int(pixel.find('ARR').text) 	      & 1)	<< 11) 
				 | ((int(pixel.find('TRIMDACR').text)	& 31)	<< 12) 
				 | ((int(pixel.find('CER').text) 	      & 1)	<< 17) 
				 | ((int(pixel.find('SP').text) 	      & 1)	<< 18) 
				 | ((int(pixel.find('SR').text) 	      & 1)	<< 19) )
		
		else:
			print "pixel number attribute in xml file, out of range"
		return val


	def _get_periphery_fromfile(self, periphery):
		val = 0
		return(  ((int(periphery.find('OM').text) 	& 3)   << 0 )
			 | ((int(periphery.find('RT').text)	& 3)   << 2 )
			 | ((int(periphery.find('SCW').text)	& 15)   << 4 )
			 | ((int(periphery.find('SH2').text)	& 15)  << 8 )
			 | ((int(periphery.find('SH1').text)	& 15)  << 12)
			 | ((int(periphery.find('CALDAC').text)	& 255) << 16)	
			 | ((int(periphery.find('THDAC').text)	& 255) << 24))

	def upload(self,show = 0,Config=1):
		cur = [None]*25
		cur[0]  = self._get_periphery_fromfile(self.xmlroot.find("periphery"))
		for pixel in self.xmlroot.findall('pixel'):
			cur[ int(pixel.attrib['n']) ] = self._get_pixel_fromfile(pixel)
		if (show):
			print "uploading:"
			print cur
		self._spi_wait()
		self._Memory_DataConf.getNode("MPA"+str(self._nmpa)).getNode("config_"+str(Config)).writeBlock(cur)
		self._hw.getNode("Configuration").getNode("num_MPA").write(0x1)
		self._hw.dispatch()

		self._hw.getNode("Configuration").getNode("mode").write(6-self._nmpa)
		self._hw.dispatch()
		#self._hw.getNode("Configuration").getNode("mode").write(6-self._nmpa)
		#self._hw.dispatch()

		self._spi_wait()
		return cur


		

	def modifypixel(self, which, what, value):
		pixel = self.xmlroot.findall('pixel')
		if isinstance(which, list):
			for n in which:
				for px in pixel:
					if int(px.attrib['n']) == n:
						px.find(what).text = str(value)
		else:	
			for px in pixel:
				if int(px.attrib['n']) == which:
					px.find(what).text = str(value)

	def modifyperiphery(self, what, value):
		per = self.xmlroot.find('periphery')
		per.find(what).text = str(value)
				





	def clean_conf(self):
		for x in range(1,25):
			self._conf.modifypixel(x,'PML', 0)
			self._conf.modifypixel(x,'ARL', 0)
			self._conf.modifypixel(x,'TRIMDACL', 15)
			self._conf.modifypixel(x,'CEL', 0)
			self._conf.modifypixel(x,'CW', 0)
			self._conf.modifypixel(x,'PMR', 0)
			self._conf.modifypixel(x,'ARR', 0)
			self._conf.modifypixel(x,'TRIMDACR', 15)
			self._conf.modifypixel(x,'CER', 0)
			self._conf.modifypixel(x,'SP',  0) 
			self._conf.modifypixel(x,'SR',  0) 


