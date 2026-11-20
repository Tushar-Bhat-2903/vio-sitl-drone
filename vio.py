import numpy as np
import cv2

# camera axes (x right, y down, z out of lens) written in drone body axes (x front, y right, z down)
# camera points straight down and the top of the image is the front of the drone
R_BC = np.array([[0, -1, 0],
                 [1,  0, 0],
                 [0,  0, 1]], dtype=float)


def rotation(roll, pitch, yaw):
    # body -> NED rotation matrix from euler angles
    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]])


class VIO:
    def __init__(self, width, height, hfov):
        self.f = (width / 2) / np.tan(hfov / 2)   # focal length in pixels
        self.center = np.array([width / 2, height / 2])
        self.pos = np.zeros(2)                    # north, east in metres
        self.prev = None

    def ground(self, pts, R_nb, height):
        # where each pixel's ray hits the ground, as north/east offset from the drone
        rays = np.column_stack(((pts - self.center) / self.f, np.ones(len(pts))))
        rays = rays @ (R_nb @ R_BC).T            # camera -> NED using the IMU attitude
        return rays[:, :2] * (height / rays[:, 2:3])

    def update(self, gray, R_nb, height):
        prev = self.prev
        self.prev = (gray, R_nb, height)
        if prev is None:
            return []
        prev_gray, prev_R, prev_h = prev

        # step 1: find corners in the last frame and track them into this frame
        p0 = cv2.goodFeaturesToTrack(prev_gray, 200, 0.01, 10)
        if p0 is None:
            return []
        p1, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, p0, None)
        good = status.ravel() == 1
        if good.sum() < 10:
            return []
        p0 = p0.reshape(-1, 2)[good]
        p1 = p1.reshape(-1, 2)[good]

        # step 2: put every corner on the ground, before and after
        g0 = self.ground(p0, prev_R, prev_h)
        g1 = self.ground(p1, R_nb, height)

        # step 3: the ground spot did not move, so the drone moved by the difference
        move = np.median(g0 - g1, axis=0)
        self.pos += move
        return p1
