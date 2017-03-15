#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3, PoseWithCovarianceStamped, PoseWithCovariance
import tf
import math

class Filter():
	def __init__(self):
		# ros node constructor
		self.pub_odom = rospy.Publisher("odom", Odometry, queue_size = 100)
		rospy.init_node("navigation_filter", log_level=rospy.DEBUG)
		imu_listener = rospy.Subscriber("imu/data", Imu, self.imu_callback)
		vel_listener = rospy.Subscriber("/navigation_velocity_smoother/raw_cmd_vel", Twist, self.vel_callback)
		init_pose_listener = rospy.Subscriber("/initialpose", PoseWithCovarianceStamped, self.set_initialpose)

		# initialize time
		self.filter_stamp_ = rospy.Time.now()
		# flags
		self.imu_active_ = False
		self.vel_active_ = False
		self.imu_initializing_ = False
		self.vel_initializing_ = False
		self.imu_counter = 0
		self.vel_counter = 0
		self.filter_counter = 0
		self.pose_initialized = False
		# parameters
		self.base_frame_ = rospy.get_param("/odom")
		self.child_frame_ = rospy.get_param("/base_frame")
		self.timeout_ = 1.0

	def set_initialpose(self,msg):
		if not self.pose_initialized:
			self.initial_pose = Pose(
				Point(msg.pose.pose.position.x,msg.pose.pose.position.y,msg.pose.pose.position.z),
				Quaternion(msg.pose.pose.orientation.x, msg.pose.pose.orientation.y,msg.pose.pose.orientation.z,msg.pose.pose.orientation.w)
				)
			self.pose = msg.pose
			self.pose_initialized = True
			rospy.loginfo("Received initial pose")
	# callback function for imu data
	def imu_callback(self,msg):
		self.imu_counter += 1
		self.imu_stamp_ = msg.header.stamp
		# add measurement
		(yaw_,pitch_,roll_) = tf.transformations.euler_from_quaternion(
			(msg.orientation.x,
			msg.orientation.y,
			msg.orientation.z,
			msg.orientation.w),
		)
		self.imu_yaw = yaw_ + math.pi
		self.imu_roll = roll_
		self.imu_pitch = pitch_
		rospy.logdebug("Received imu data: Yaw:%f, Roll:%f, Pitch:%f" %(self.imu_yaw,self.imu_roll,self.imu_pitch))
		# activate imu
		if not self.imu_active_ :
			if not self.imu_initializing_ :
				self.imu_initializing_ = True
				self.imu_initial_yaw = yaw_ + math.pi
				self.imu_init_stamp_ = self.imu_stamp_
				rospy.loginfo("Initializing Imu sensor")
			if self.filter_stamp_ >= self.imu_init_stamp_ :
				self.imu_active_ = True
				self.imu_initializing_ = False
				rospy.loginfo("Imu sensor activated")

	def vel_callback(self,msg):
		self.vel_counter += 1
		self.vel_stamp_ = rospy.Time.now()
		# add measurement
		self.vel_linear_x = msg.linear.x
		self.vel_angular_z = msg.angular.z
		rospy.logdebug("Received velocity data: %f, stamp:%f" %(self.vel_linear_x,self.vel_stamp_.to_sec()))

		# activate velocity controller
		if not self.vel_active_ :
			if not self.vel_initializing_ :
				self.vel_initializing_ = True
				self.vel_init_stamp_ = self.vel_stamp_
				self.pre_vel_stamp_ = rospy.Time.from_sec(rospy.get_time())
				rospy.loginfo("Initializing velocity controller")
			if self.filter_stamp_ >= self.vel_init_stamp_ :
				self.vel_active_ = True
				self.vel_initializing_ = False
				rospy.loginfo("Velocity controller activated")		

	def odom_estimator(self):
		# check for timing issue
		if (self.imu_initializing_ or self.imu_active_) and (self.vel_initializing_ and self.vel_active_) :
			diff = abs((self.imu_stamp_ - self.vel_stamp_).to_sec())
			if diff > self.timeout_:
				rospy.logerr("Timestamps of velocity controller and imu are %f seconds apart" % diff)

		self.filter_stamp_ = rospy.Time.now()

		# check which sensors are still active
		if (self.imu_initializing_ or self.imu_active_) and ((rospy.Time.now() - self.imu_stamp_).to_sec() > self.timeout_) :
			self.imu_initializing_ = False
			self.imu_active_ = False
			rospy.loginfo("Imu is not active anymore")
			rospy.loginfo("Imu has been inactive for %f" %(rospy.Time.now() - self.imu_stamp_).to_sec())

		if (self.vel_initializing_ or self.vel_active_) and ((rospy.Time.now() - self.vel_stamp_).to_sec() > self.timeout_) :
			self.vel_initializing_ = False
			self.vel_active_ = False
			rospy.loginfo("Velocity controller is not active anymore")
			rospy.loginfo("Velocity controller has been inactive for %f" %(rospy.Time.now() - self.vel_stamp_).to_sec())

		# only update filter when one of the sensors is active
		if self.imu_active_ or self.vel_active_ :
			if self.imu_active_:
				self.filter_stamp_ = min(self.imu_stamp_, self.filter_stamp_)
			if self.vel_active_:
				self.filter_stamp_ = min(self.vel_stamp_, self.filter_stamp_)

		# update odometry when velocity controller is not active
		if (not self.vel_active_) and self.imu_active_ and self.pose_initialized:
			self.filter_counter += 1
			odom = Odometry()
			odom.header.seq = self.filter_counter
			odom.header.stamp = self.filter_stamp_
			odom.header.frame_id = self.base_frame_
			odom.child_frame_id = self.child_frame_
			position = (
				self.pose.pose.position.x,
				self.pose.pose.position.y,
				0.0
			) 
			(roll,pitch,yaw) = tf.transformations.euler_from_quaternion(
				(self.initial_pose.orientation.x,
				self.initial_pose.orientation.y,
				self.initial_pose.orientation.z,
				self.initial_pose.orientation.w),
				'sxyz'
			)
			rospy.logdebug("yaw:%f,pitch:%f,roll:%f" %(self.initial_pose.orientation.x,pitch,roll))
			orientation = tf.transformations.quaternion_from_euler(
				self.imu_roll + roll,
				self.imu_pitch + pitch,
				self.imu_yaw + yaw - self.imu_initial_yaw,
				'rxyz'
			)
			orientation = Quaternion(
				orientation[0],
				orientation[1],
				orientation[2],
				orientation[3]
			)
			self.pose.pose = Pose(
				Point(position[0],position[1],position[2]), 
				orientation
			)
			odom.pose.pose = self.pose.pose
			odom.twist.twist = Twist(Vector3(0,0,0),Vector3(0,0,0))
			self.filter_update(odom)
			rospy.loginfo("Waiting for velocity controller...")

		# update odometry when both sensors are active
		if self.vel_active_ and self.imu_active_ and self.pose_initialized:
			self.filter_counter += 1

			dt = (self.vel_stamp_ - self.pre_vel_stamp_).to_sec()
			self.pre_vel_stamp_ = self.vel_stamp_
			rospy.logdebug("dt:%f" %dt)

			(roll,pitch,yaw) = tf.transformations.euler_from_quaternion(
				(self.initial_pose.orientation.x,
				self.initial_pose.orientation.y,
				self.initial_pose.orientation.z,
				self.initial_pose.orientation.w),
				'sxyz'
			)
			orientation = tf.transformations.quaternion_from_euler(
				self.imu_roll + roll,
				self.imu_pitch + pitch,
				self.imu_yaw + yaw - self.imu_initial_yaw,
				'rxyz'
			)
			orientation = Quaternion(
				orientation[0],
				orientation[1],
				orientation[2],
				orientation[3]
			)			

			position = (
				self.pose.pose.position.x + dt * self.vel_linear_x * math.cos(self.imu_yaw+yaw-self.imu_initial_yaw),
				self.pose.pose.position.y + dt * self.vel_linear_x * math.sin(self.imu_yaw+yaw-self.imu_initial_yaw),
				0.0
			) 

			self.pose.pose = Pose(
				Point(position[0],position[1],position[2]), 
				orientation
			)

			odom = Odometry()
			odom.header.seq	= self.filter_counter
			odom.header.stamp = self.filter_stamp_
			odom.header.frame_id = self.base_frame_
			odom.child_frame_id = self.child_frame_
			odom.pose.pose = self.pose.pose
			odom.twist.twist = Twist(
				Vector3(self.vel_linear_x, 0., 0.),
				Vector3(0., 0., self.vel_angular_z)
			)
			self.filter_update(odom)
			rospy.logdebug("Updating filter...")

	def filter_update(self,odom):
		#publish transform and topic
		self.pub_odom.publish(odom)
		tf_broadcaster = tf.TransformBroadcaster()
		tf_broadcaster.sendTransform(
			(odom.pose.pose.position.x, odom.pose.pose.position.y, odom.pose.pose.position.z),
			(odom.pose.pose.orientation.x, odom.pose.pose.orientation.y, odom.pose.pose.orientation.z, self.pose.pose.orientation.w),
			self.filter_stamp_,
			self.child_frame_,
			self.base_frame_
		)


if __name__ == "__main__":
	try:
		my_filter = Filter()
		rospy.loginfo("Starting filter...")
	except Exception as e:
		print e
		exit(0)

	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		my_filter.odom_estimator()
		rate.sleep()


