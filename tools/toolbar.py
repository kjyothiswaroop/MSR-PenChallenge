import cv2
import numpy as np

class toolBar:

    def __init__(self, windowName):
        self.windowName = windowName
        self.ranges = {
            "H_min": 179, "S_min": 255, "V_min": 255,
            "H_max": 179, "S_max": 255, "V_max": 255,
            "Clipping_Distance": 10
        }

        # Initialize values dict
        self.values = {
            "H_min": 125, "S_min": 50, "V_min": 50,
            "H_max": 155, "S_max": 255, "V_max": 255,
            "Clipping_Distance": 1
        }

        # Create trackbars
        for key, max_val in self.ranges.items():
            cv2.createTrackbar(key, self.windowName, self.values[key], max_val,lambda val, k=key: self.set_value(k, val))

    def set_value(self, k, val):
        self.values[k] = val

    def get_value(self, k):
        return self.values[k]

    def get_hsv_bounds(self):
        
        lower = np.array([self.values["H_min"],self.values["S_min"], self.values["V_min"]])
        upper = np.array([self.values["H_max"],self.values["S_max"],self.values["V_max"]])

        return lower, upper
