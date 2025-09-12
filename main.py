#!/usr/bin/env python3

import cv2
import pyrealsense2 as rs
import numpy as np
import imageProcessor.pipeline as pipeline
import argparse
import imageProcessor.streamer as streamer
import tools.toolbar as toolbar

def main():
    parser = argparse.ArgumentParser(description="Aligned Image streamer")
    parser.add_argument("--mode", choices=["live", "record", "playback"], default="live",
                        help="Pipeline mode: live (default), record, or playback")
    parser.add_argument("--filename", type=str, default=None,
                        help="Filename for record/playback (.bag)")

    args = parser.parse_args()

    windowName = "Realsense Stream"
    cv2.namedWindow(windowName)
    cv2.waitKey(1)

    tools = toolbar.toolBar(windowName)
    
    with pipeline.pipeLineManager(mode=args.mode,file_name=args.filename) as pm:
        streamerObj = streamer.Streamer(pm,tools)
        streamerObj.stream()
        centroid = streamerObj.getCentroid()

        print(centroid)
        print(streamerObj.get3Dcords(centroid))


if __name__ == "__main__":
    main()