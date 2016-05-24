"""
Robotritons testing version of gps navigation.

Purpose: Use reliable GPS data to navigate the vehicle
Requirements: 
Use: 

Resources:
"""
import sys
import time
from GPSConfigBackEnd import *
import VehiclePWMModule

ubl = U_blox()
'''
mess_CFG_PRT_IO = [0xb5,0x62,0x06,0x00,0x01,0x00,0x04,0x0b,0x25]
mess_CFG_MSG1 = [0xb5,0x62,0x06,0x01,0x02,0x00,0x01,0x02,0x0c,0x35]#this is for a NavPosllh
mess_CFG_MSG2 = [0xb5,0x62,0x06,0x01,0x02,0x00,0x01,0x03,0x0d,0x36]#this is for a NavStatus
mess_CFG_MSG8D = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x12,0xb9]#this is to disable a NavPosllh
mess_CFG_MSG8E = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x01,0x00,0x13,0xbb]#this is to re-enable a NavPosllh
messGet_CFG_PRT_SPI = [0xb5,0x62,0x06,0x00,0x14,0x00,0x04, "19more","chka","chkb"]
'''

def GPSNavInit():
	#reset the Ublox messages
	CFGmsg8_NAVposllh_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x12,0xb9]#Disable Ublox from publishing a NAVposllh	
	CFGmsg8_NAVstatus_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x13,0xc0]#Disable Ublox from publishing a NAVstatus
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVposllh_no)
		ubl.bus.xfer2(CFGmsg8_NAVstatus_no)
	
	#Enable the gps status messages
	CFGmsg8_NAVstatus_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x01,0x00,0x14,0xc2]#Enable Ublox to publish a NAVstatus
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVstatus_yes)
	
	#I made the NavStatusMessage method and parse_ubx method of ubl also return a value (in addition to text).
	#Wait until we have a confirmed GPS fix
	while (True):
		buffer = ubl.bus.xfer2([100])
		for byte in buffer:
			ubl.scan_ubx(byte)
			if(ubl.mess_queue.empty() != True):
				fix = ubl.parse_ubx()
				if (fix != None):
					print 'fix', fix, '\n'
					if((fix['fStatus'] == 2) or (fix['fStatus'] == 3) or (fix['fStatus'] == 4)):
						print 'good fix', '\n'
						break
		else:
			continue
		break
	#To fix this nested while:for: loop I should make this a function and use return in the innermost loop allowing me to exit to the top

	#After confirmed fix, disable Navstatus messages
	CFGmsg8_NAVstatus_no = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x13,0xc0]#Disable Ublox from publishing a NAVstatus
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVstatus_no)
		
	#Wiggle weels to indicate done init
	vehicle_servo.steer(45)
	time.sleep(0.5)
	vehicle_servo.steer(105)
	time.sleep(0.5)
	vehicle_servo.center()

def NAVposllhUpdate():
	#Start the NAVposllh messages
	'''
	CFGmsg8_NAVposllh_yes = [0xb5,0x62,0x06,0x01,0x08,0x00,0x01,0x02,0x00,0x00,0x00,0x00,0x01,0x00,0x13,0xbb]#Enable Ublox to publish a NAVposllh
	for x in range(0, 10):
		ubl.bus.xfer2(CFGmsg8_NAVposllh_yes)
	'''
	msg = [0xb5, 0x62, 0x06, 0x01, 0x03, 0x00, 0x01, 0x02, 0x01, 0x0e, 0x47]
	for x in range(0,10):
		ubl.bus.xfer2(msg)

	#Move forward and back slowly until established valuable horizontal accuraccy
	while (True):
		buffer = ubl.bus.xfer2([100])
		for byte in buffer:
			vehicle_esc.accel(3) #Move back if it wasn't accurate enough
			ubl.scan_ubx(byte)
			if(ubl.mess_queue.empty() != True):
				pos = ubl.parse_ubx()
				if (pos != None):
					print 'pos',pos,'\n'
					print(msg)
					print 'hAcc',pos['hAcc'],'\n'
					if(pos['hAcc'] <= 10):
						print 'good acc \n'
						break
		else:
			vehicle_esc.accel(-10) #Move back if it wasn't accurate enough
			continue
		break
#ERROR Once we include both accel(-10) and accel(3) in either order in this above loop, accel somehow enters an infinite loop
#Also ERROR making the accel statements go in the same direction but different speeds isn't updating either direction and stops backwards
	print 'passed acc \n'

	#Stop shennanigans now that we've got an accurate gps readings
	vehicle_esc.stop()
	
	#Grab the current gps location
	buffer = ubl.bus.xfer2([100])
	for byte in buffer:
		ubl.scan_ubx(byte)
		if(ubl.mess_queue.empty() != True):
			pos = ubl.parse_ubx()
	
	print pos, '\n'
	#Know next location
	#calculate next waypoint heading
	#Set course to move towards next waypoint



vehicle_servo = VehiclePWMModule.vehiclePWM("servo")
vehicle_esc = VehiclePWMModule.vehiclePWM("esc")
x=1
while(True):
	try:
		while (x):
			vehicle_esc.stop()
			vehicle_servo.rest()
			vehicle_servo.center()
			#Watch out for running GPSNavInit a second time when only
			#NavPosllh messages are enabled because "fix" will return
			#a NavPosllh dictionary but the GPSNavInit expects a NavStatus dictionary with the key "fStatus"
			GPSNavInit()
			x = 0
			print 'once'
		#Testing and in progress
		NAVposllhUpdate()
		
		#While (not at waypoint):
		#	GPSNavUpdate()
	except KeyboardInterrupt:
		vehicle_esc.stop()
		vehicle_servo.rest()
		sys.exit()
