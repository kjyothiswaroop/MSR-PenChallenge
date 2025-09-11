#!/usr/bin/env python3

import cv2
import pyrealsense2 as rs
import numpy as np
import pipeline
import argparse
import streamer

def main():
    parser = argparse.ArgumentParser(description="Aligned Image streamer")
    parser.add_argument("--mode", choices=["live", "record", "playback"], default="live",
                        help="Pipeline mode: live (default), record, or playback")
    parser.add_argument("--filename", type=str, default=None,
                        help="Filename for record/playback (.bag)")

    args = parser.parse_args()


    with pipeline.pipeLineManager(mode=args.mode,file_name=args.filename) as pm:
        streamerObj = streamer.Streamer(pm,clipping_distance=4)
        streamerObj.stream()

        

if __name__ == "__main__":
    main()