import cv2
import pyrealsense2 as rs
import numpy as np
import imageProcessor.pipeline as pipeline

class Streamer:

    def __init__(self,pm,tools,clipping_distance=1):
       self.pipeline = pm.pipeline
       self.profile = pm.profile
       self.pm = pm
       self.tools = tools
       self.centroids = []

       depth_sensor = self.profile.get_device().first_depth_sensor()
       self.depth_scale = depth_sensor.get_depth_scale()


       self.clipping_distance = clipping_distance / self.depth_scale

       self.align = rs.align(rs.stream.color)

       self.playback_device = self.profile.get_device().as_playback()

    def get_depth_and_color(self,frame):

        if frame is None:
            return None, None

        aligned_frames = self.align.process(frame)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        self.aligned_depth_frame = aligned_depth_frame
        self.color_frame = color_frame

        return aligned_depth_frame, color_frame
    
    def process_frame(self,depth_frame,color_frame):
        
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        grey_color = 153
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > self.clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        mask,converted_img = self.convertToHSV(bg_removed)

        if self.contour_object(mask,converted_img):
            center,contour = self.contour_object(mask,converted_img)
            if center is not None:
                c_x, c_y = center
                # Draw contour and centroid
                cv2.drawContours(converted_img, [contour], -1, (0, 255, 0), 2)
                cv2.circle(converted_img, center, 5, (0, 0, 255), -1)
                #cv2.putText(converted_img, f"({c_x}, {c_y})", (c_x + 10, c_y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                self.centroids.append((c_x,c_y))
                if self.get3Dcords((c_x,c_y)):
                    X,Y,Z = self.get3Dcords((c_x,c_y))
                    cv2.putText(converted_img, f"({X}, {Y},{Z})", (c_x + 10, c_y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        

                
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        image_processed = np.hstack((bg_removed, converted_img))

        return image_processed
    

    def convertToHSV(self,frame):

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lower, upper = self.tools.get_hsv_bounds()
        mask = cv2.inRange(hsv,lower,upper)
        hsv_result = cv2.bitwise_and(frame,frame,mask=mask)

        return mask,hsv_result

    def contour_object(self,mask,frame):

        contours,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest_contour = max(contours,key=cv2.contourArea)

        if cv2.contourArea(largest_contour) < 500:
            return None
        
        moments = cv2.moments(largest_contour)
        if(moments["m00"] == 0):
            return None
        
        c_x = int(moments["m10"] / moments["m00"])
        c_y = int(moments["m01"] / moments["m00"])

        return (c_x,c_y),largest_contour


    def stream(self):

        while True:

            frameset = self.pm.getFrames()
            if frameset is None:
                break

            self.clipping_distance = self.tools.get_value("Clipping_Distance") / self.depth_scale

            depth_frame,color_frame = self.get_depth_and_color(frameset)
            processed_image = self.process_frame(depth_frame,color_frame)

            cv2.imshow("Realsense Stream", processed_image)

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                break

        cv2.destroyAllWindows()
    
    def getCentroid(self):

        centroid_x = 0
        centroid_y = 0
        if self.centroids:
            for centroid in self.centroids:
                centroid_x += centroid[0]
                centroid_y += centroid[1]

            mean_cx,mean_cy = int(centroid_x/len(self.centroids)) , int(centroid_y/len(self.centroids))

            return (mean_cx,mean_cy)
        
    
    def get3Dcords(self,centroid):

        if centroid is None:
            return None
        
        x , y = centroid
        Z = self.aligned_depth_frame.get_distance(x,y)

        if Z == 0:
            return None
        
        prof = self.profile.get_stream(rs.stream.color)
        intrinsic = prof.as_video_stream_profile().get_intrinsics()

        X,Y,Z = rs.rs2_deproject_pixel_to_point(intrinsic, [x,y], Z)

        return (X,Y,Z)
        
