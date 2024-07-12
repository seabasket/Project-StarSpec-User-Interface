#!/bin/bash

# start INDI venv
source ~/venv_indi_pylibcamera/bin/activate

#init py camera, mount, and ZWO camera, will run continuously
indiserver -v indi_pylibcamera ./indi/build/drivers/telescope/indi_celestron_gps indi_asi_ccd

