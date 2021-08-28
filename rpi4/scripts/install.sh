#!/bin/bash

FMSG="EMAR Mini installation terminated!"

printf -- 'This script will install the EMAR Mini on your device.\n';
printf -- '\033[33m WARNING: This is an inteteractive installation, please follow instructions provided. \033[0m\n';

read -p "Proceed (y/n)? " proceed
if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
	printf -- 'Installing the EMAR Mini....\n';
    sudo ufw allow 22
    sudo ufw allow OpenSSH
    sudo ufw enable
    sudo ufw status
    sudo apt install fail2ban
    sudo mv /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
    sudo rm /etc/fail2ban/action.d/ufw.conf
    sudo touch /etc/fail2ban/action.d/ufw.conf
    echo "[Definition]" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  enabled  = true" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  actionstart =" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  actionstop =" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  actioncheck =" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  actionban = ufw insert 1 deny from <ip> to any" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    echo "  actionunban = ufw delete deny from <ip> to any" | sudo tee -a /etc/fail2ban/action.d/ufw.conf
    sudo nano /etc/fail2ban/action.d/ufw.conf
    sudo sed -i -- "s#banaction = iptables-multiport#banaction = ufw#g" /etc/fail2ban/jail.local
    sudo nano /etc/fail2ban/jail.local
    sudo fail2ban-client restart
    sudo fail2ban-client status
    sudo apt install build-essential cmake unzip pkg-config
    sudo apt install cmake
    sudo apt install python3-dev
    sudo apt install python3-gi
    sudo apt install python3-pip
    sudo apt install python3-dev python3-rpi.gpio
    sudo apt install libjpeg-dev libpng-dev libtiff-dev
    sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    sudo apt install libxvidcore-dev libx264-dev
    sudo apt install libgtk-3-dev
    sudo apt install libcanberra-gtk*
    sudo apt install libatlas-base-dev gfortran
    sudo pip3 install flask
    sudo pip3 install paho-mqtt
    sudo pip3 install psutil
    sudo pip3 install numpy
    sudo pip3 install requests
    sudo pip3 install zmq
    wget https://github.com/IntelRealSense/librealsense/raw/master/scripts/libuvc_installation.sh
    sudo sed -i -- "s/cmake ../ -DFORCE_LIBUVC=true -DCMAKE_BUILD_TYPE=release/cmake ../ -DFORCE_LIBUVC=true -DCMAKE_BUILD_TYPE=release -DBUILD_PYTHON_BINDINGS=bool:true/g" libuvc_installation.sh
    ./libuvc_installation.sh
    cd
    wget https://storage.openvinotoolkit.org/repositories/openvino/packages/2021.4/l_openvino_toolkit_runtime_raspbian_p_2021.4.582.tgz
    tar -xf l_openvino_toolkit_runtime_raspbian_p_2021.4.582.tgz
    mv l_openvino_toolkit_runtime_raspbian_p_2021.4.582 openvino
    echo 'source ~/openvino/bin/setupvars.sh' >> ~/.bashrc
    source ~/.bashrc
    sudo usermod -a -G users "$(whoami)"
    cd
    sh openvino/install_dependencies/install_NCS_udev_rules.sh
	printf -- '\033[32m SUCCESS: EMAR Mini installed successfully! \033[0m\n';
	exit 0
else
	echo $FMSG;
	exit 1
fi