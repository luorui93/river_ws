#!/usr/bin/env python
import rospy
import os
from speed_control.msg import Speed

def emergency_stop():
	print("STOP!")
	#msg = Speed()
	#pub = rospy.Publisher('wheelchair_speed', Speed, queue_size = 1000)
	os.system("rostopic pub -1 /wheelchair_speed speed_control/Speed -- '{header: {seq: 0, stamp: now, frame_id: 'wheelchair'}, velocity: 0.0, direction: 0.0}'")
	#pub.publish(msg)
	#rospy.sleep(3)

def set_speed():
	pub = rospy.Publisher('wheelchair_speed', Speed, queue_size = 1000, latch=True)
	rospy.init_node('speed_controller')
	r = rospy.Rate(1) # 10 hz
	msg = Speed()
	msg.velocity = 0.1   # voltage
	msg.direction = 0.1  # voltage

	prev_msg = Speed()

	while not rospy.is_shutdown():
	#	rospy.loginfo(msg)
		if prev_msg == msg:
			continue
		pub.publish(msg)
		prev_msg = msg
		#r.sleep()

	#rospy.on_shutdown(emergency_stop)
	#rospy.on_shutdown(lambda:pub.publish(msg))

if __name__ == "__main__":
	try:
		set_speed()
	except rospy.ROSInterruptException as e:
		print e

