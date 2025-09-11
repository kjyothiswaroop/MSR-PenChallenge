import cv2
import pyrealsense2 as rs
import numpy as np

class AlignImages:

    def __init__(self,mode,file_name,clipping_distance=1):
        self.pipeline = rs.pipeline()   
        self.config = rs.config()
        self.mode = mode
        self.filename = file_name
        self.clipping_distance_meters = clipping_distance

        if self.mode != "playback":
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = self.config.resolve(pipeline_wrapper)

            self.device = pipeline_profile.get_device()
            self.device_product_line = str(self.device.get_info(rs.camera_info.product_line))

            rgb = False
            for sensor in self.device.sensors:
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

        self.getDepthImage()
        self.alignImage()

        if self.mode == "playback":
            self.playback_device = self.profile.get_device().as_playback()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pipeline.stop()
        cv2.destroyAllWindows()
        return False


    def getDepthImage(self):
        depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        self.clipping_distance = self.clipping_distance_meters / self.depth_scale

    def alignImage(self):
        self.align = rs.align(rs.stream.color)

    def streamLoop(self):

         while True:
            
            frames = self.pipeline.wait_for_frames()

            if self.mode == "playback":
                current_position = self.playback_device.get_position()
                total_duration = self.playback_device.get_duration().total_seconds() * 1e9  # Convert to nanoseconds
                if current_position >= total_duration:
                    print("Playback finished")
                    break

            aligned_frames = self.align.process(frames)
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not aligned_depth_frame or not color_frame:
                continue
            
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            grey_color = 153
            depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
            bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

            # Render images:
            #   depth align to color on left
            #   depth on right
            
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            images = np.hstack((bg_removed, depth_colormap))
            cv2.namedWindow('Align Example', cv2.WINDOW_NORMAL)
            cv2.imshow('Align Example', images)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                break