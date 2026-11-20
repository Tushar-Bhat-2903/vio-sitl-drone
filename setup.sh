#!/bin/bash
# one time install on Ubuntu 22.04 (takes a while)
set -e

sudo apt update
sudo apt install -y git wget lsb-release gnupg python3-pip python3-opencv python3-matplotlib

# gazebo harmonic
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
sudo apt update
sudo apt install -y gz-harmonic python3-gz-transport13 python3-gz-msgs10 libgz-sim8-dev rapidjson-dev \
    libopencv-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl

# ardupilot SITL
cd ~
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y

# ardupilot gazebo plugin
cd ~
git clone https://github.com/ArduPilot/ardupilot_gazebo
cd ardupilot_gazebo
mkdir -p build && cd build
GZ_VERSION=harmonic cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo
make -j4

pip3 install --user pymavlink

echo 'export GZ_VERSION=harmonic' >> ~/.bashrc
echo 'export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/ardupilot_gazebo/build:$GZ_SIM_SYSTEM_PLUGIN_PATH' >> ~/.bashrc
echo 'export GZ_SIM_RESOURCE_PATH=$HOME/ardupilot_gazebo/models:$HOME/ardupilot_gazebo/worlds:$GZ_SIM_RESOURCE_PATH' >> ~/.bashrc
echo 'done, open a new terminal (or log out and back in)'
