#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3, PoseWithCovarianceStamped
import tf
import math

def kinect_callback(msg):
	x = msg.pose.pose.position.z
	y = msg.pose.pose.position.x
	z = -msg.pose.pose.position.y

	rotation = tf.transformations.euler_from_quaternion(
			[msg.pose.pose.orientation.x,
			msg.pose.pose.orientation.y,
			msg.pose.pose.orientation.z,
			msg.pose.pose.orientation.w]
		)

	rotation_new = tf.transformations.quaternion_from_euler(
			-rotation[2],
			-rotation[0],
			rotation[1]
		)

	br = tf.TransformBroadcaster()
	br.sendTransform(
		(x,y,z),
		rotation_new,
		msg.header.stamp,
		"base_link",
		"odom"
		)

def map_odom_callback(msg):
	br = tf.TransformBroadcaster()
	rate = rospy.Rate(10.0)
	#pose = (msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z)
	#rotation = (msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)
	rotation = (0,0,0,1)
	translation = (0,0,0)
	while not rospy.is_shutdown():
		br.sendTransform(
			translation,
			rotation,
			rospy.Time.now(),
			"odom",
			"map"
		)
		rate.sleep()


if __name__ == "__main__":
	rospy.init_node("tf_broadcaster")
	kinect_listener = rospy.Subscriber("kinect_odometer/odometry", Odometry, kinect_callback)
	map_odom_listener = rospy.Subscriber("initialpose", PoseWithCovarianceStamped, map_odom_callback)
	rospy.spin()
