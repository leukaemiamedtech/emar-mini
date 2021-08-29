#!/bin/bash

FMSG="EMAR Mini installation terminated!"

printf -- 'This script will install the EMAR Mini on your device.\n';
printf -- '\033[33m WARNING: This is an inteteractive installation, please follow instructions provided. \033[0m\n';

read -p "Proceed (y/n)? " proceed
if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
	printf -- 'Installing the EMAR Mini....\n';
    sudo apt install cmake
    sudo apt install mpg123
    sudo apt install python3-gi
    sudo apt install python3-dev python3-rpi.gpio
    sudo pip3 install flask
    sudo pip3 install gtts
    sudo pip3 install regex
    sudo pip3 install pydbus
    sudo pip3 install zmq
    wget https://github.com/IntelRealSense/librealsense/raw/master/scripts/libuvc_installation.sh
    chmod +x libuvc_installation.sh
    sudo apt install build-essential cmake unzip pkg-config
    sudo apt install libjpeg-dev libpng-dev libtiff-dev
    sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    sudo apt install libxvidcore-dev libx264-dev
    sudo apt install libgtk-3-dev
    sudo apt install libcanberra-gtk*
    sudo apt install libatlas-base-dev gfortran
    sudo apt install python3-dev
    cd
    wget https://storage.openvinotoolkit.org/repositories/openvino/packages/2021.4/l_openvino_toolkit_runtime_raspbian_p_2021.4.582.tgz
    tar -xf l_openvino_toolkit_runtime_raspbian_p_2021.4.582.tgz
    mv l_openvino_toolkit_runtime_raspbian_p_2021.4.582 openvino
    echo 'source ~/openvino/bin/setupvars.sh' >> ~/.bashrc
    source ~/.bashrc
    printf -- '\033[32m SUCCESS: EMAR Mini installed successfully! \033[0m\n';
    exit 0
else
    echo $FMSG;
    exit 1
fi