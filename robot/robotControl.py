from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from interbotix_xs_modules.xs_robot.gripper import InterbotixGripperXS
from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
import numpy as np
# The robot object is what you use to control the robot

class Robot:

    def __init__(self):
        self.robot = InterbotixManipulatorXS("px100", "arm", "gripper")
        self.known_poses = [(.2, 0, .2), (.1, -.1, .2), (.1, .1, .2), (.1, .2, .1), (.25, 0, .1)]

    def __enter__(self):
        robot_startup()
        return self

    def __exit__(self,exc_type, exc_value, traceback):
        self.robotSleep()
        self.release()
        robot_shutdown()
        return False

    def moveRobot(self,pose):
        x,y,z = pose
        self.robot.arm.set_ee_pose_components(x,y,z)

    def graspObject(self):
        self.robot.gripper.grasp()
    
    def release(self):
        self.robot.gripper.release()

    def robotHome(self):
        self.robot.arm.go_to_home_pose()
    
    def robotSleep(self):
        self.robot.arm.go_to_sleep_pose()

    def rotateJoint(self,joint,value):
        self.robot.arm.set_single_joint_position(joint,value)
    
    def get_ee_Pose(self):
        poseMatrix = self.robot.arm.get_ee_pose()
        ee_pos_x ,ee_pos_y,ee_pos_z = poseMatrix[0][3],poseMatrix[1][3],poseMatrix[2][3]

        return (ee_pos_x,ee_pos_y,ee_pos_z)
    
    def pickPen(self,pose):

        self.moveRobot(pose)
        self.graspObject()
        self.robotSleep()
        self.release()
    

    
