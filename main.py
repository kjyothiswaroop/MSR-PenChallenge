#!/usr/bin/env python3

import cv2
import pyrealsense2 as rs
import numpy as np
import imageProcessor.pipeline as pipeline
import argparse
import imageProcessor.streamer as streamer
import tools.toolbar as toolbar
from scipy.spatial.transform import Rotation as R
import imageProcessor.calibration as calibration
import robot.robotControl as robot
import json
import time
import signal
import sys

def signal_handler(sig, frame):
    print("\nStopping robot workflow...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    parser = argparse.ArgumentParser(description="Aligned Image streamer")
    parser.add_argument("--mode", choices=["live", "record", "playback"], default="live",
                        help="Pipeline mode: live (default), record, or playback")
    parser.add_argument("--filename", type=str, default=None,
                        help="Filename for record/playback (.bag)")
    parser.add_argument("--calibrate", type=bool, default=False,help="Flag to enable/disable calibration")
    parser.add_argument("--stream",type=bool,default=False,help="Flag to enable/disable stream of images")
    parser.add_argument("--pickPen",type=bool,default=False,help="Flag to enable/disable stream of images")

    args = parser.parse_args()

    windowName = "Realsense Stream"
    cv2.namedWindow(windowName)
    # cv2.waitKey(1)

    tools = toolbar.toolBar(windowName)
    
    with pipeline.pipeLineManager(mode=args.mode,file_name=args.filename) as pm:
        streamerObj = streamer.Streamer(pm,tools)

        if(args.stream):
            streamerObj.stream()

        with robot.Robot() as robotArm:
            robotArm.release()
            if(args.calibrate):
                calibFile = "calibFiles/calib.json"
                calibData = []
                robotArm.graspObject()
                robotArm.robotSleep()

                for pose in robotArm.known_poses:
                    robotArm.moveRobot(pose)
                    input("Press Enter to continue.....")
                    img = streamerObj.procImage()
                    cv2.imshow(windowName, img)
                    print("Showing calibration preview... press Enter in the terminal to continue.")
                    cv2.waitKey(1)   # ensure it actually paints
                    input() 

                    ee_pose = robotArm.get_ee_Pose()
                    centroid = streamerObj.getCentroid()
                    centroid3D = streamerObj.getValid3Dcords()

                    calibData.append({"commanded_pose":pose,"ee_pose":ee_pose,"centroid3D":centroid3D})
                
                with open(calibFile,"w") as f:
                    json.dump(calibData,f)
                robotArm.robotSleep()

            if(args.pickPen):

                calibrator = calibration.Calibration()
                calibrator.loadJSON("calibFiles/calib.json")
                Rot, translate = calibrator.getTransforms()
                robotArm.robotSleep()
                robotArm.release()
                print(Rot)
                print(translate)

                while True:
                    img_proc = streamerObj.procImage()
                    cv2.imshow(windowName, img_proc)
                    print("Showing preview... press Enter in the terminal to continue.")
                    # cv2.waitKey(1)   # ensure it actually paints
                    input() 

                    current_centroid = streamerObj.getCentroid()
                    current3DCentroid = streamerObj.getValid3Dcords()

                    if current3DCentroid != (0,0,0):
                        q_Cords = np.dot(Rot,np.array(current3DCentroid)) + translate
                        print(q_Cords)
                        # cylin_cords = robotArm.calculateCylindricalCords(q_Cords)
                        # robotArm.pickPen(cylin_cords)
                        robotArm.pickPen(q_Cords)
                        time.sleep(0.1)
                    else :
                        print("Pen Not found!, Waiting..........")
                    
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                        break

                
        cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()