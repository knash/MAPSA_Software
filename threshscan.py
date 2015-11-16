
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
import ROOT
from ROOT import TH2F, TCanvas, TTree, TBranch, TFile
#from ROOT import TGraph
import sys, select, os, array,subprocess
from array import array
#import ROOT
#from ROOT import TGraph
import datetime
saveout = sys.stdout



commands = []
i=0
thresh = 80
for i in range(0,44):
	#thresh=thresharray[i]
	
	print thresh
	for j in range(0,1):
		commands.append('python daq.py -s default -m 0 -t '+str(thresh)+' -y Novapack_2_120V_T'+str(thresh)+' -r both -v True -u False')

	thresh+=4
for s in commands :
	print 'executing ' + s
	subprocess.call( [s], shell=True )
