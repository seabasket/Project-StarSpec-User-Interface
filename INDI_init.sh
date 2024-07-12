#!/bin/bash

#initiate INDI virtual environment
source ~/venv_indi_pylibcamera/bin/activate

#init picamera, mount, and ZWO camera (will run continuously)
indiserver -v indi_pylibcamera ./indi/build/drivers/telescope/indi_celestron_gps indi_asi_ccd
