# VIO drone in ArduPilot SITL + Gazebo (no ROS)

| file | what it does |
|---|---|
| setup.sh | installs Gazebo Harmonic, ArduPilot SITL and the ardupilot_gazebo plugin (task 1) |
| make_world.py, world_template.sdf | world with a textured ground and the Iris with a downward camera |
| fly_mission.py | takeoff and landing (task 2), `--square 20` also flies a square |
| vio.py | the visual inertial odometry |
| vio_sitl.py | gets the Iris camera from Gazebo and attitude/GPS from ArduPilot, runs VIO, saves log.csv (task 3) |
| plot_compare.py | GPS vs VIO plot and error (task 4) |

## Run

    bash setup.sh                 # once, then open a new terminal
    python3 make_world.py         # once

Terminal 1 - Gazebo

    gz sim -v4 -r world/vio_world.sdf

Terminal 2 - ArduPilot SITL

    sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --out 127.0.0.1:14551

Task 2 - Terminal 3

    python3 fly_mission.py

Task 3 - Terminal 3, then Terminal 4

    python3 vio_sitl.py
    python3 fly_mission.py --square 20

After landing press q in the camera window. Then for task 4

    python3 plot_compare.py

## How the VIO works

The camera looks straight down. Height comes from ArduPilot, attitude (roll, pitch, yaw) from the IMU.

1. Find corners in the last frame and track them into the new frame (Lucas-Kanade optical flow).
2. Turn each corner into a ray using the camera focal length and the IMU attitude, and find where it hits the ground (ground is flat, height is known).
3. The ground spot did not move, so the drone moved by (spot before - spot after). Take the median over all corners and add it to the position.

GPS is only used as the starting point and as the reference for the comparison.
