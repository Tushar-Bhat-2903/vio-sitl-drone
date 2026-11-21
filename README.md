# Visual inertial odometry on an ArduPilot SITL drone in Gazebo

![VIO vs GPS](vio_vs_gps.png)

Top view of both paths, north and east against time, and the distance between VIO and GPS over time.

## Videos

| Task | Link |
|---|---|
| 1. Takeoff and landing |https://drive.google.com/file/d/13pYd_9B3QAZiIeQfyG02QTDcNRfVFqeX/view|
| 2. Camera VIO while flying the square |https://drive.google.com/file/d/17YG8Qb2CK7NwdHkgiRnGHTyuaUI4xIiN/view?usp=sharing|

## What is in the repo

| File | Purpose |
|---|---|
| `setup.sh` | Installs Gazebo Harmonic, ArduPilot SITL and the ardupilot_gazebo plugin (task 1) |
| `make_world.py` | Generates a textured ground image and writes `world/vio_world.sdf` |
| `world_template.sdf` | World with the Iris, ground plane and a 640x480 downward camera |
| `fly_mission.py` | Takeoff and landing over MAVLink (task 2). `--square 20` also flies a square |
| `vio.py` | The visual inertial odometry itself (about 25 lines of core code) |
| `vio_sitl.py` | Reads the camera from Gazebo and attitude, height and GPS from ArduPilot, runs VIO, writes `log.csv` (task 3) |
| `plot_compare.py` | Draws the comparison plot and prints RMSE (task 4) |
| `vio_vs_gps.png` | Plot from my own run |

## Install (task 1)

Run once:

```bash
bash setup.sh
```

Generate the world, 

```bash
python3 make_world.py
```

## Commands to run

### Terminal 1: Gazebo

```bash
cd ~/Downloads/vio_sitl
gz sim -v4 -r world/vio_world.sdf
```

### Terminal 2: ArduPilot SITL

```bash
cd ~/ardupilot
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --out 127.0.0.1:14551
```

For the VIO flight (task 3)

```bash
cd ~/ardupilot
sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --out 127.0.0.1:14551 --add-param-file=$HOME/Downloads/vio_sitl/vio.parm
```

Use the plain command for task 2.

### Task 2: takeoff and landing

Terminal 3:

```bash
cd ~/Downloads/vio_sitl
python3 fly_mission.py
```

The drone arms, climbs to 10 m, hovers for 5 seconds and lands.

### Task 3: flying the square on VIO

The drone navigates on the VIO position. GPS is also logged.

```bash
cd ~/Downloads/vio_sitl
python3 vio_sitl.py
```

Terminal 4:

```bash
cd ~/Downloads/vio_sitl
python3 fly_mission.py --square 20
```

In the camera window, green dots are the tracked corners and the yellow text shows VIO and GPS north/east in metres.

### Task 4: GPS vs VIO comparison

```bash
cd ~/Downloads/vio_sitl
python3 plot_compare.py
```
## How the VIO works

The camera looks straight down. Height comes from ArduPilot and roll, pitch and yaw come from ArduPilot's attitude estimate (the IMU part). For each new frame:

1. Find up to 200 corners in the previous frame and track them into the new frame. 
2. For each corner, turn the pixel into a ray with the camera focal length, rotate the ray by the drone's attitude, and find where it hits the flat ground. Do this for the old pixel (old attitude and height) and the new pixel (new attitude and height).
3. Its move is the median of (old ground offset minus new ground offset) over all corners. Add it to the position.

## Results

| Metric | Value |
|---|---|
| RMSE, VIO vs GPS | 0.59 m ||

## Limits

- The ground is assumed flat and the height is trusted. On real terrain the scale would be wrong.
- Attitude and image are paired by "latest available", without timestamp matching.
- It is odometry only. There is no loop closure or any correction, so errors that do add up stay.
- It needs texture and light. A blank floor would give no corners. The generated ground has random shapes for that reason, and shadows are switched off because a moving shadow would fake motion.
