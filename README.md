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

### Task 4: GPS vs VIO comparison

```bash
cd ~/Downloads/vio_sitl
python3 plot_compare.py
```
## How the VIO works

The camera points straight down at the ground. ArduPilot tells the program the drone's height and its tilt (roll, pitch and yaw). The tilt comes from the motion sensor, which is the "inertial" part. For every new camera picture, the program does this:

1. **Find and follow corners.** It picks up to 200 sharp corners in the previous picture and finds where each one went in the new picture.
2. **Put the corners on the ground.** For each corner it works out where on the flat ground that pixel is looking. It does this once for the old picture, using the old tilt and height, and once for the new picture, using the new tilt and height. Using the tilt stops a leaning drone from being mistaken for a moving one.
3. **Measure the move.** A real spot on the ground does not move, so if its ground position changed between the pictures, the drone must have moved. The program takes the old ground position minus the new one for every corner, and uses the middle value (the median) so a few badly tracked corners are ignored. Then it adds that move to the running position.

## Results

| Metric | Value |
|---|---|
| RMSE, VIO vs GPS | 0.56 m ||
