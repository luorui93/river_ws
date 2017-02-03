#!/usr/bin/env python
import rospy
from speed_control.msg import Speed

def set_speed():
	pub = rospy.Publisher('wheelchair_speed', Speed, queue_size = 1000)
	rospy.init_node('speed_controller')
	r = rospy.Rate(10) # 10 hz
	msg = Speed()
	msg.velocity = 7.0   # voltage
	msg.direction = -1.0  # voltage

	while not rospy.is_shutdown():
	#	rospy.loginfo(msg)
		pub.publish(msg)
		r.sleep()

if __name__ == "__main__":
	try:
		set_speed()
	except rospy.ROSInterruptException as e:
		print e

