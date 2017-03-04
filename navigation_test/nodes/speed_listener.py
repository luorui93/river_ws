#!/usr/bin/env python

import roslib
roslib.load_manifest('navigation_test')

import rospy
from geometry_msgs.msg import Twist
import tf

speed_x = 0.0
speed_y = 0.0
speed_r = 0.0

def callback(msg):
    speed_x = msg.linear.x
    speed_y = msg.linear.y
    speed_r = msg.angular.z
    rospy.loginfo("speed value heard x= %f,y= %f, r=%f", speed_x, speed_y, speed_z)

    
if __name__ == '__main__':
    rospy.init_node('speed_listener', anonymous=False)
    rospy.Subscriber('navigation_velocity_smoother/raw_cmd_vel', Twist, callback)
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        br.sendTransform((0.0, 0.0, 0.0),
                         (0.0, 0.0, 0.0, 1.0),
                         rospy.Time.now(),
                         "odom",
                         "map")
        rate.sleep()
