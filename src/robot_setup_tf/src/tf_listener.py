#! /usr/bin/env python

import time
import rospy
import tf 
from geometry_msgs.msg import PointStamped

#def callback(self):


if __name__ == "__main__":
	rospy.init_node("tf_listener")
	listener = tf.TransformListener()

	tf_publisher = rospy.Publisher('tf_point', PointStamped, queue_size = 1000)
	# time.sleep(1)
	laser_point = PointStamped()


	listener.waitForTransform('base_laser','base_link',rospy.Time(),rospy.Duration(5))

	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		now = rospy.Time.now()
		listener.waitForTransform('base_laser','base_link',now,rospy.Duration(2))
		
		laser_point.header.stamp = now 
		laser_point.header.frame_id = 'base_laser'
		laser_point.point.x = 1.0
		laser_point.point.y = 0.4
		laser_point.point.z = 0.1
		# Point = listener.lookupTransform('base_laser','base_link',rospy.Time())

		new_point = listener.transformPoint('base_link', laser_point)
		tf_publisher.publish(new_point)

		rate.sleep()
		# print Point
	#rospy.spin()