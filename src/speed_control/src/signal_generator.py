#!/usr/bin/env python

#import phidget library
import sys
from time import sleep
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.Analog import Analog
from Phidgets.Phidget import PhidgetLogLevel

#import ROS library
import rospy
from speed_control.msg import Speed
from geometry_msgs.msg import Twist

def emergencystop():
	print("emergency stop!")
	analog.setEnabled(0,False)
	analog.setEnabled(1,False)
	analog.setVoltage(0, 0)	    
	analog.setVoltage(1, 0)

#Information Display Function
def displayDeviceInfo():
    print("|------------|----------------------------------|--------------|------------|")
    print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    print("|------------|----------------------------------|--------------|------------|")
    print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (analog.isAttached(), analog.getDeviceName(), analog.getSerialNum(), analog.getDeviceVersion()))
    print("|------------|----------------------------------|--------------|------------|")
    print("Number of analog outputs: %i" % (analog.getOutputCount()))
    print("Maximum output voltage: %d" % (analog.getVoltageMax(0)))
    print("Minimum output voltage: %d" % (analog.getVoltageMin(0)))

#Event Handler Callback Functions
def AnalogAttached(e):
    attached = e.device
    print("Analog %i Attached!" % (attached.getSerialNum()))

def AnalogDetached(e):
    detached = e.device
    print("Analog %i Detached!" % (detached.getSerialNum()))

def AnalogError(e):
    try:
        source = e.device
        print("Analog %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def callback(data):
	#rospy.loginfo("Received data:\n Velocity:%4.2f, Direction:%4.2f" % (data.velocity,data.direction))
	try:
		velocity = data.linear.x * 9.8 
		direction = -data.angular.z * 6.6 #minus -> left turn positive -> right turn
		analog.setVoltage(0, velocity)	    
		analog.setVoltage(1, direction)
		pub = rospy.Publisher("output_speed", Speed, queue_size = 100)
		speed = Speed()
		speed.velocity = velocity
		speed.direction = direction
		pub.publish(speed)

	#This error message needs to be modifed /Rui
	except PhidgetException as e:
	    print("Phidget Exception %i: %s" % (e.code, e.details))
	    print("Exiting....")
	    sys.exit(1)

def listener():
	rospy.init_node("signal_generator")
	# rospy.Subscriber("wheelchair_teleop/cmd_vel",Twist,callback)
	rospy.Subscriber("/navigation_velocity_smoother/raw_cmd_vel", Twist, callback)

	rospy.spin()
	rospy.on_shutdown(emergencystop)

if __name__ == "__main__":	
	#Create an accelerometer object
	try:
	    analog = Analog()
	except RuntimeError as e:
	    print("Runtime Exception: %s" % e.details)  
	    print("Exiting....")
	    exit(1)
	try:
	    analog.setOnAttachHandler(AnalogAttached)
	    analog.setOnDetachHandler(AnalogDetached)
	    analog.setOnErrorhandler(AnalogError)
	except PhidgetException as e:
		print("Phidget Exception %i: %s" % (e.code, e.details))
		print("Exiting....")
		exit(1)

	print("Opening phidget object....")

	try:
	    analog.openPhidget()
	except PhidgetException as e:
	    print("Phidget Exception %i: %s" % (e.code, e.details))
	    print("Exiting....")
	    exit(1)

	print("Waiting for attach....")

	try:
	    analog.waitForAttach(10000)
	except Exception as e:
	    print("Phidget Exception %i: %s" % (e.code, e.details))
	    try:
	        analog.closePhidget()
	    except PhidgetException as e:
	        print("Phidget Exception %i: %s" % (e.code, e.details))
	        print("Exiting....")
	        exit(1)
	    print("Exiting....")
	    exit(1)
	else:
	    displayDeviceInfo()

	try:
		print("Enabling Velocity Channel (0)...")
		analog.setEnabled(0, True)
		print("Enabling Velocity Channel (1)...")
		analog.setEnabled(1, True)
	except Exception as e:
		print "Can't enable channel\n"
		print e
	listener()
