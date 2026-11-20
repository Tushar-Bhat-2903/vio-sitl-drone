# task 2: takeoff and land. with --square 20 it also flies a 20 m square (used for the VIO test)
import argparse
import time
from pymavlink import mavutil

parser = argparse.ArgumentParser()
parser.add_argument('--alt', type=float, default=10)
parser.add_argument('--square', type=float, default=0)
args = parser.parse_args()

mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
mav.wait_heartbeat()
print('connected')


def set_rate(msg_id, hz):
    mav.mav.command_long_send(mav.target_system, mav.target_component,
                              mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                              msg_id, 1e6 / hz, 0, 0, 0, 0, 0)


set_rate(mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 10)
set_rate(mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 10)

mav.param_set_send('WPNAV_SPEED', 300)      # fly at 3 m/s
mav.param_set_send('WP_YAW_BEHAVIOR', 0)    # keep the nose pointing the same way

mav.set_mode(mav.mode_mapping()['GUIDED'])

print('arming, can take a minute while GPS locks')
while not mav.motors_armed():
    mav.mav.command_long_send(mav.target_system, mav.target_component,
                              mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    mav.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
    time.sleep(1)
print('armed')

mav.mav.command_long_send(mav.target_system, mav.target_component,
                          mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, args.alt)
while True:
    alt = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True).relative_alt / 1000
    print('altitude %.1f m' % alt)
    if alt > 0.95 * args.alt:
        break
time.sleep(5)

if args.square > 0:
    start = mav.recv_match(type='LOCAL_POSITION_NED', blocking=True)
    s = args.square
    for north, east in [(s, 0), (s, s), (0, s), (0, 0)]:
        x, y = start.x + north, start.y + east
        print('going to', north, east)
        while True:
            # only position is used, velocity/accel/yaw fields are ignored by the mask
            mav.mav.set_position_target_local_ned_send(
                0, mav.target_system, mav.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED, 0b110111111000,
                x, y, start.z, 0, 0, 0, 0, 0, 0, 0, 0)
            p = mav.recv_match(type='LOCAL_POSITION_NED', blocking=True)
            if abs(p.x - x) < 1 and abs(p.y - y) < 1:
                break
        time.sleep(2)

print('landing')
mav.set_mode(mav.mode_mapping()['LAND'])
while mav.motors_armed():
    mav.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
print('landed')
