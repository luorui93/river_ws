#!/usr/bin/env python

## Simple myo demo that listens to std_msgs/UInt8 poses published 
## to the 'myo_gest' topic

import rospy
from std_msgs.msg import UInt8, String
from geometry_msgs.msg import Twist, Vector3
from speed_control.msg import Speed
from ros_myo.msg import MyoArm

# Marked for removal
import sys, select, termios, tty

########## Data Enums ###########
# MyoArm.arm___________________ #
#    UNKNOWN        = 0 	#
#    RIGHT          = 1		#
#    Left           = 2		#
# MyoArm.xdir___________________#
#    UNKNOWN        = 0		#
#    X_TOWARD_WRIST = 1		#
#    X_TOWARD_ELBOW = 2		#
# myo_gest UInt8________________#
#    REST           = 0		#
#    FIST           = 1		#
#    WAVE_IN        = 2		#
#    WAVE_OUT       = 3		#
#    FINGERS_SPREAD = 4		#
#    THUMB_TO_PINKY = 5		#
#    UNKNOWN        = 255	#
#################################

userMsg = """
Control Wheelchair via Myo
----------------------------
Spread fingers: go forward
Fist: go back
Wave left: go left
Wave right: go right
Rest: stop smoothly

No speed control

CTRL-C to quit
"""

speed = 2.5
turn = 2.5


if __name__ == '__main__':

    global armState
    global xDirState
    global target_speed
    global target_turn
    global lineCnt
    armState = 0
    target_speed = 0
    target_turn = 0
    rospy.init_node('wheelchair_myo')

    velocityPub = rospy.Publisher('~cmd_vel', Speed, queue_size=5)

    # set the global arm states
    def setArm(data):
        global armState
        global xDirState

        armState = data.arm
        xDirState = data.xdir
        rospy.sleep(2.0)


    # Use the calibrated Myo gestures to drive the wheelchair
    def drive(gest):
        if gest.data == 0:  # REST
            print("stop")
            target_speed = 0
            target_turn = 0
        elif gest.data == 1:  # FIST
            print("go back")
            target_speed = -1.0 * speed
            target_turn = 0
        elif gest.data == 2 and armState == 1:  # WAVE_IN, RIGHT arm
            print("go left")
            target_speed = 0
            target_turn = -1.0 * turn
        elif gest.data == 2 and armState == 2:  # WAVE_IN, LEFT arm
            print("go right")
            target_speed = 0
            target_turn = 1.0 * turn
        elif gest.data == 3 and armState == 1:  # WAVE_OUT, RIGHT arm
            print("go right")
            target_speed = 0
            target_turn = 1.0 * turn
        elif gest.data == 3 and armState == 2:  # WAVE_OUT, LEFT arm
            print("go left")
            target_speed = 0
            target_turn = -1.0 * turn
        elif gest.data == 4:  # FINGERS_SPREAD
            print("go forward")
            target_speed = 1.0 * speed
            target_turn = 0

        lineCnt = lineCnt + 1


    rospy.Subscriber("myo_arm", MyoArm, setArm)
    rospy.Subscriber("myo_gest", UInt8, drive)
    rospy.loginfo('Please sync the Myo')

    lineCnt = 0
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    try:
        print(userMsg)

        while(1):
            # Re-display the user instructions every 15 lines
            if (lineCnt > 15):
                print(userMsg)
                lineCnt = 0

            #0.5 -> acceleration, need to be big enough to overcome the friction
            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 0.5 )
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 0.5 )
            else:
                control_speed = target_speed

            if target_turn > control_turn:
                control_turn = min( target_turn, control_turn + 0.5 )
            elif target_turn < control_turn:
                control_turn = max( target_turn, control_turn - 0.5 )
            else:
                control_turn = target_turn

            msg = Speed()
            msg.velocity = control_speed
            msg.direction = control_turn
            velocityPub.publish(msg)

    except Exception as e:
        print "Control error"
        print e

    finally:
        msg = Speed()
        msg.velocity = 0.0
        msg.direction = 0.0
        velocityPub.publish(msg)


    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()


