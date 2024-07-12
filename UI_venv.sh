#!/bin/bash
echo "Test!"

#initiate user interface virtual environment
source STSC/STSCvenv/bin/activate

#navigate to UI file
cd STSC/STSCvenv/UI

#run user interface file in python
python StarSpec_UI.py
