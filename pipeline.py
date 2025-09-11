import cv2
import pyrealsense2 as rs
import numpy as np

class pipeLineManager:

    def __init__(self,mode,file_name):
        self.pipeline = rs.pipeline()   
        self.config = rs.config()
        self.mode = mode
        self.filename = file_name


        if self.mode != "playback":
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = self.config.resolve(pipeline_wrapper)

            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            rgb = False
            for sensor in device.sensors:
                if sensor.get_info(rs.camera_info.name) == 'RGB Camera':
                    rgb = True

            if not rgb:
                print("RGB CAMERA IS NEEDED")
                exit(0)

    def __enter__(self):
        
        if self.mode == "playback":
            if not self.filename:
                raise ValueError("Filename required for playback mode")
            self.config.enable_device_from_file(self.filename)

        else :
            self.config.enable_stream(rs.stream.depth,640,480,rs.format.z16, 30)
            self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

            if self.mode == "record":
                if not self.filename:
                    raise ValueError("Filename required for record mode")
                self.config.enable_record_to_file(self.filename)

        self.profile = self.pipeline.start(self.config)

        if self.mode == "playback":
            self.playback_device = self.profile.get_device().as_playback()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pipeline.stop()
        return False

    def getFrames(self):

        frames = self.pipeline.wait_for_frames()

        if self.mode == "playback":
            current_position = self.playback_device.get_position()
            total_duration = self.playback_device.get_duration().total_seconds() * 1e9  # Convert to nanoseconds
            if current_position >= total_duration:
                print("Playback finished")
                return None
            
        return frames