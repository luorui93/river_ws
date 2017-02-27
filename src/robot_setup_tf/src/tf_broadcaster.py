#! /usr/bin/env python

import rospy
import tf

if __name__ == "__main__":
	rospy.init_node("tf_broadcaster")
	br = tf.TransformBroadcaster()
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		br.sendTransform((0.1,0,0.2),
						 tf.transformations.quaternion_from_euler(0,0,0),
						 rospy.Time.now(),
						 "base_laser",
						 "base_link")
		rate.sleep()
	rospy.spin()
	