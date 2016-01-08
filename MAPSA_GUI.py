#
# Simple command launcher for testbeam   -JD 12-8-2015
#
import sys, select, os, array,subprocess
from Tkinter import *
#import serial
import time


class TBeamControl:
    def __init__(self):

        self.setting = 'default'
        self.readout = 'both'
        self.formatstring = 'noprocessing'
        self.threshold = '90'
        self.testbeam_clock = 'glib'
        self.title = 'none'
        self.shutter_duration = '500000' 
        self.normalize = 'False'
        self.direction = 'glib'



    def exit(self):
        print("Exit by Exit button in UI\n") 
        sys.exit(0)

    def poweron(self,state):
        if (state == 1) :
            print('turn on\n')
            os.system("python power.py -s on")
        elif (state == 0) :
            print('turn off\n')
            os.system("python power.py -s off")
        else:
            print "Something went wrong."

    def calibration(self):
        print('Calibration pushed in UI')
        self.shutter_duration = e7.get()
        commandstring = "python calibration.py -w %s" % (self.shutter_duration)
        os.system(commandstring) 

    def daq(self):
        print('DAQ pushed in UI')
        self.setting = e1.get()
        self.readout = e2.get()
        self.formatstring = e3.get()
        self.threshold = e4.get()
        self.testbeam_clock = e5.get()
        self.title = e6.get()
        self.shutter_duration = e7.get()
        self.normalize = e8.get()
        self.direction = e9.get()
        commandstring = "python daq.py -s %s -r %s -f %s -t %s -T %s -y %s -w %s -N %s -D %s" % (self.setting, self.readout, self.formatstring, self.threshold, self.testbeam_clock, self.title, self.shutter_duration, self.normalize,self.direction)
	print("pushing function " + commandstring)
        os.system(commandstring) 

    


tbeam = TBeamControl()
root = Tk()
tbeamui = Frame(root)
tbeamui.grid()


root.title("Simple TestBeam script launcher")
root.geometry("420x450");
#text_box = Entry(tbeamui, justify=RIGHT)
#text_box.grid(row = 0, column = 0, columnspan = 3, pady = 5)
#text_box.insert(0, "0")

button_exit = Button(tbeamui, text="Exit")
button_exit["command"]=lambda: tbeam.exit()
button_exit.grid(row=1,column=0, pady=5)

button_poweron = Button(tbeamui, text="Power ON")
button_poweron["command"]=lambda: tbeam.poweron(1)
button_poweron.grid(row=2,column=1, pady=5)

button_poweroff = Button(tbeamui, text="Power OFF")
button_poweroff["command"]=lambda: tbeam.poweron(0)
button_poweroff.grid(row=2,column=2, pady=5)

lab1 =  Label(tbeamui, width=20,text="Setting",anchor='w')
lab1.grid(row=3,column=1,pady=5)
e1=Entry(tbeamui)
e1.insert(10,tbeam.setting);
e1.grid(row=3,column=2,pady=5)

lab2 =  Label(tbeamui, width=20,text="Readout",anchor='w')
lab2.grid(row=4,column=1,pady=5)
e2=Entry(tbeamui)
e2.insert(10,tbeam.readout);
e2.grid(row=4,column=2,pady=5)

lab3 =  Label(tbeamui, width=20,text="Format",anchor='w')
lab3.grid(row=5,column=1,pady=5)
e3=Entry(tbeamui)
e3.insert(10,tbeam.formatstring);
e3.grid(row=5,column=2,pady=5)

lab4 =  Label(tbeamui, width=20,text="Threshold",anchor='w')
lab4.grid(row=6,column=1,pady=5)
e4=Entry(tbeamui)
e4.insert(10,tbeam.threshold);
e4.grid(row=6,column=2,pady=5)

lab5 =  Label(tbeamui, width=20,text="Testbeam clock",anchor='w')
lab5.grid(row=7,column=1,pady=5)
e5=Entry(tbeamui)
e5.insert(10,tbeam.testbeam_clock);
e5.grid(row=7,column=2,pady=5)

lab6 =  Label(tbeamui, width=20,text="Title",anchor='w')
lab6.grid(row=8,column=1,pady=5)
e6=Entry(tbeamui)
e6.insert(10,tbeam.title);
e6.grid(row=8,column=2,pady=5)

lab7 =  Label(tbeamui, width=20,text="Shutter duration",anchor='w')
lab7.grid(row=9,column=1,pady=5)
e7=Entry(tbeamui)
e7.insert(10,tbeam.shutter_duration);
e7.grid(row=9,column=2,pady=5)

lab8 =  Label(tbeamui, width=20,text="Normalize",anchor='w')
lab8.grid(row=10,column=1,pady=5)
e8=Entry(tbeamui)
e8.insert(10,tbeam.normalize);
e8.grid(row=10,column=2,pady=5)


lab9 =  Label(tbeamui, width=20,text="Strip direction",anchor='w')
lab9.grid(row=11,column=1,pady=5)
e9=Entry(tbeamui)
e9.insert(10,tbeam.direction);
e9.grid(row=11,column=2,pady=5)


button_calibration = Button(tbeamui, text="Run Calibration")
button_calibration["command"]=lambda: tbeam.calibration()
button_calibration.grid(row=12,column=1, pady=5)

button_daq = Button(tbeamui, text="Run DAQ")
button_daq["command"]=lambda: tbeam.daq()
button_daq.grid(row=12,column=2, pady=5)

commands = 	[
			'export LD_LIBRARY_PATH=/opt/cactus/lib:$LD_LIBRARY_PATH',
			'export PATH=/opt/cactus/bin:$PATH'
		]
for s in commands :
		subprocess.call( [s], shell=True )


root.mainloop()
