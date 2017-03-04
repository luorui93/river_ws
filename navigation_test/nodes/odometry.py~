#!/usr/bin/env python

import roslib
roslib.load_manifest('navigation_test')

import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import tf
import math

speed_x = 0.0
speed_r = 0.0
distance_x =0.0
distance_y =0.0
direction_z = 0.0
t = rospy.Time()

# get twist value and integrate
def callback(msg):
    global t
    global speed_x
    global speed_r
    global distance_x
    global distance_y
    global direction_z
    speed_x = msg.linear.x
    speed_r = msg.angular.z
    time = rospy.Time.now()
    if t.secs == 0:
        dt = rospy.Time(0)
    else:
        dt = time - t
    t = time
    direction_z += speed_r *dt.secs + speed_r * dt.nsecs/1000000000
    distance_x +=  math.cos(direction_z)*(speed_x * dt.secs + speed_x * dt.nsecs/1000000000)
    distance_y +=  math.sin(direction_z)*(speed_x * dt.secs + speed_x * dt.nsecs/1000000000)
    # rospy.loginfo("%f, %f, %f", distance_x, distance_y, direction_z)
    
    
    
# publish odometry_msg
def odometry_talker():
    global speed_x
    global speed_r
    global distance_x
    global distance_y
    global direction_z
	
    pub_odom = rospy.Publisher('odom', Odometry, queue_size =5)
    rospy.init_node('odom_talker')
    rospy.Subscriber('/navigation_velocity_smoother/raw_cmd_vel', Twist, callback)

    
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10)
    Odom = Odometry();
    while not rospy.is_shutdown():
       t = rospy.Time.now().secs
       Odom.header.stamp = rospy.Time.now()
       Odom.header.frame_id = "odom"
       Odom.child_frame_id = "base_footprint"
       Odom.pose.pose.position.x = distance_x 
       Odom.pose.pose.position.y = distance_y
       Odom.pose.pose.position.z = 0.0
    
       Odom.twist.twist.linear.x = speed_x
       Odom.twist.twist.angular.z = speed_r
    
       x = Odom.pose.pose.position.x
       y = Odom.pose.pose.position.y
       z = Odom.pose.pose.position.z

       quat = tf.transformations.quaternion_from_euler(0, 0, direction_z)
       Odom.pose.pose.orientation.x = quat[0]
       Odom.pose.pose.orientation.y = quat[1]
       Odom.pose.pose.orientation.z = quat[2]
       Odom.pose.pose.orientation.w = quat[3]
       br.sendTransform((x, y, z),
                        (quat[0], quat[1], quat[2], quat[3]),
                        rospy.Time.now(),
                        "base_footprint",
                        "odom")
       pub_odom.publish(Odom)
       rate.sleep()
       print ("%f", x)

if __name__ == '__main__':
    try:
        odometry_talker()
    except rospy.ROSInterruptException:
        pass
        
