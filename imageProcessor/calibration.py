from scipy.spatial.transform import Rotation as R
import numpy as np
import json

class Calibration:

    def __init__(self):
        self.points_ee = []
        self.point_camera = []

    def loadJSON(self,filename):
        calibfile = filename

        with open(calibfile,"r") as f:
            calibData = json.load(f)
        self.points_ee = np.array([tuple(entry["ee_pose"]) for entry in calibData])
        self.points_camera = np.array([tuple(entry["centroid3D"]) for entry in calibData])
        
    def getTransforms(self):
        # Center the points (remove centroid)
        camera_centroid = self.points_camera.mean(axis=0)
        ee_centroid = self.points_ee.mean(axis=0)
        camera_centered = self.points_camera - camera_centroid
        ee_centered = self.points_ee - ee_centroid

        # Compute best-fit rotation using Kabsch (via SciPy)
        rot, _ = R.align_vectors(ee_centered, camera_centered)
        rotationMatrix = rot.as_matrix()

        # Compute translation
        translationMatrix = ee_centroid - rotationMatrix @ camera_centroid

        return rotationMatrix, translationMatrix