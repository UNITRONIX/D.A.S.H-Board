#!/bin/bash
cd "$(dirname "$0")"
sudo git config --global --add safe.directory /opt/D.A.S.H-Board
sudo apt-get install python3-dev
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade setuptools
sudo pip3 install --upgrade wheel
sudo pip3 install -r requirements.txt
sudo python3 main.py