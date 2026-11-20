# task 3: read the iris camera from gazebo, attitude/altitude/GPS from ardupilot, run VIO and log it
import csv
import time
import numpy as np
import cv2
from pymavlink import mavutil
from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image
from vio import VIO, rotation

HFOV = 1.047          # same as in world_template.sdf
EARTH_RADIUS = 6378137

mav = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
mav.wait_heartbeat()
for msg_id, hz in [(mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 30),
                   (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 10),
                   (mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 10)]:
    mav.mav.command_long_send(mav.target_system, mav.target_component,
                              mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                              msg_id, 1e6 / hz, 0, 0, 0, 0, 0)

attitude = None
altitude = 0.0
home = None
gps = np.zeros(2)       # GPS position as north, east in metres from the first fix


def read_mavlink():
    global attitude, altitude, home, gps
    while True:
        msg = mav.recv_match(blocking=False)
        if msg is None:
            return
        kind = msg.get_type()
        if kind == 'ATTITUDE':
            attitude = rotation(msg.roll, msg.pitch, msg.yaw)
        elif kind == 'GLOBAL_POSITION_INT':
            altitude = msg.relative_alt / 1000
        elif kind == 'GPS_RAW_INT' and msg.fix_type >= 3:
            lat, lon = msg.lat / 1e7, msg.lon / 1e7
            if home is None:
                home = (lat, lon)
            north = np.radians(lat - home[0]) * EARTH_RADIUS
            east = np.radians(lon - home[1]) * EARTH_RADIUS * np.cos(np.radians(home[0]))
            gps = np.array([north, east])


# gazebo calls this in its own thread, so just keep the newest frame here
latest = None


def on_image(msg):
    global latest
    latest = msg


node = Node()
node.subscribe(Image, '/iris/camera', on_image)

vio = None
rows = []
start = time.time()
print('running, press q in the camera window to stop and save')

while True:
    read_mavlink()
    if latest is None:
        time.sleep(0.005)
        continue
    msg = latest
    latest = None

    frame = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, 3)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    view = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # only run VIO in the air, on the ground the camera sees almost nothing
    if attitude is not None and home is not None and altitude > 1.5:
        if vio is None:
            vio = VIO(msg.width, msg.height, HFOV)
            vio.pos = gps.copy()      # start from the same point as GPS
        points = vio.update(gray, attitude, altitude)
        for x, y in points:
            cv2.circle(view, (int(x), int(y)), 3, (0, 255, 0), -1)
        rows.append([time.time() - start, vio.pos[0], vio.pos[1], gps[0], gps[1], altitude])
        text = 'VIO N %.1f E %.1f   GPS N %.1f E %.1f   alt %.1f' % (
            vio.pos[0], vio.pos[1], gps[0], gps[1], altitude)
        cv2.putText(view, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    cv2.imshow('iris camera', view)
    if cv2.waitKey(1) == ord('q'):
        break

with open('log.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['t', 'vio_n', 'vio_e', 'gps_n', 'gps_e', 'alt'])
    writer.writerows(rows)
print('saved', len(rows), 'rows to log.csv')
