#Extra functions, mainly due to the fact that we are using an old python version 

import math
import uhal
import binascii
from uasic import *
import numpy as np
import elementtree.ElementTree as ET
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment

def byte_to_binary(n):
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary(h):
    binnumber = ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))
    while len(binnumber)<32:
	binnumber = '0' + binnumber
    return binnumber

def frmt(x):
    Y = str(hex(x)).replace('0x','')
    num = len(Y)
    if num & 0x1:
	Y = '0'+Y
    return Y
	
	
