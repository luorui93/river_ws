#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3
import tf
import math


class Odometry_broadcaster():
	def __init__(self):
		self.pub_odom = rospy.Publisher("odom", Odometry, queue_size = 1000)
		rospy.init_node("odom_broadcaster")
		imu_attitude = rospy.Subscriber("imu/data", Imu, self.pos_estimator)
		# imu_data = rospy.Subscriber("imu/data", IMU, self.broadcaster)
		self.velocity = [0.,0.]
		self.pos = [0.,0.]
		self.time = rospy.Time.now()
		self.init_yaw = 0.0
		self.stop_count = 0

	def pos_estimator(self,data):
		quaternion = (
    		data.orientation.x,
    		data.orientation.y,
    		data.orientation.z,
    		data.orientation.w
    	)
		euler = tf.transformations.euler_from_quaternion(quaternion)  # in radians
		yaw = euler[0]
		roll = euler[1]
		pitch = euler[2]
		
		th = yaw - self.init_yaw

		accel = int(data.linear_acceleration.x * 10) / 10.0
		# print accel
		delta_t = data.header.stamp.to_sec() - self.time.to_sec()
		# print delta_t

		self.pos[0] += self.velocity[0] * delta_t #+ 1/2 * accel * math.cos(th) * pow(delta_t,2)
		self.pos[1] += self.velocity[1] * delta_t #+ 1/2 * accel * math.sin(th) * pow(delta_t,2)
		x = self.pos[0]
		y = self.pos[1]

		self.velocity[0] += (accel * delta_t) * math.cos(th)
		self.velocity[1] += (accel * delta_t) * math.sin(th)

		#clear the velocity buffer after 2 seconds of stop
		if accel == 0:
			self.stop_count += 1
			if self.stop_count == 50 * 1: #50HZ * 2s
				self.stop_count = 0
				self.velocity[0] = 0
				self.velocity[1] = 0
		else:
		 	self.stop_count = 0

		# print self.stop_count
		vx = self.velocity[0]
		vy = self.velocity[1]

		self.time = data.header.stamp

		Odom = Odometry()
		br = tf.TransformBroadcaster()
		
		Odom.header.stamp = data.header.stamp
		Odom.header.frame_id = "odom"
		Odom.child_frame_id = "base_footprint"
		Odom.pose.pose = Pose(Point(x, y, 0.), data.orientation)	
		Odom.twist.twist = Twist(Vector3(vx,vy,0),Vector3(0,0,th))

		rotation = tf.transformations.quaternion_from_euler(0,0,th + math.pi)
		br.sendTransform(
			(0,0,0.),
			rotation,
			data.header.stamp,
			"base_footprint",
			"odom"
			)
		self.pub_odom.publish(Odom)

if __name__ == "__main__":
	try:
		odometry = Odometry_broadcaster()
	except Exception as e:
		print e
		
	rospy.spin()

