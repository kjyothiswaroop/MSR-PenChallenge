import cv2
import pyrealsense2 as rs
import numpy as np
import pipeline

class Streamer:

    def __init__(self,pm,clipping_distance=1):
       self.pipeline = pm.pipeline
       self.profile = pm.profile
       self.pm = pm

       depth_sensor = self.profile.get_device().first_depth_sensor()
       depth_scale = depth_sensor.get_depth_scale()

       self.clipping_distance = clipping_distance / depth_scale

       self.align = rs.align(rs.stream.color)

       self.playback_device = self.profile.get_device().as_playback()

    def get_depth_and_color(self,frame):

        if frame is None:
            return None, None

        aligned_frames = self.align.process(frame)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        return aligned_depth_frame, color_frame
    
    def process_frame(self,depth_frame,color_frame):
        
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        grey_color = 153
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        image_processed = np.hstack((bg_removed, depth_colormap))

        return image_processed
    
    def stream(self):

        while True:

            frameset = self.pm.getFrames()
            if frameset is None:
                break

            depth_frame,color_frame = self.get_depth_and_color(frameset)
            processed_image = self.process_frame(depth_frame,color_frame)

            cv2.imshow("Realsense Stream", processed_image)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                break

        cv2.destroyAllWindows()
    