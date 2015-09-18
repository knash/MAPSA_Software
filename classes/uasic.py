#!/usr/bin/python


from random import randint
import sys, os, getopt
import unittest
import time

from math import sqrt, pow
import logging
#from utils import *

try: 
  import uhal
except:
  logging.error("Unable to load uhal module")
       
class uasic:
  def __init__(self,connection="file://connections_test.xml",device="board0"):
    self._manager=uhal.ConnectionManager( connection)
    self._hw=self._manager.getDevice ( device )
    
