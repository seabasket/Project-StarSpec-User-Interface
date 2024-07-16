import subprocess
import time

#run KSTARS_init.sh to initialize INDI server
KSTARS_init_path = "./KSTARS_init.sh"
KSTARS_init_command = f"gnome-terminal -- bash -c '{KSTARS_init_path}; exec bash'"
KSTARS_init_process = subprocess.Popen(KSTARS_init_command, shell=True)
print("Initializing KSTARS...")
time.sleep(6)

#run INDI_init.sh to initizlize INDI server
INDI_init_path = "./INDI_init.sh"
INDI_init_command = f"gnome-terminal -- bash -c '{INDI_init_path}; exec bash'"
INDI_init_process = subprocess.Popen(INDI_init_command, shell=True)
print("Initializing INDI Server...")
time.sleep(6)

import os
from gi.repository import GObject as gobject
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
from PIL import ImageTk, Image
import cv2
from cv2 import *
import dbus
from dbus import glib
import threading

def ZWOLiveThreadFunc():
    while True:
        if ZWOLiveActive:
            #get exposure time for image capture
            try:
                exptime = int(ZWOexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1
            takeZWOPicture(exptime, "/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO", "ZLIVE") #take image
    
            #display image
            test_image = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO/ZLIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=test_image, size=(470, 315))
            label = ctk.CTkLabel(live_loop_frame, text="", image=Z_live_test)
            label.place(x=100, y=60) 
            time.sleep(exptime)
        time.sleep(1)
    
def PILiveThreadFunc():
    while True:
        if PILiveActive:
            #get exposure time for image capture
            try:
                exptime = int(PIexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1
            takePIPicture(exptime, "/home/starspec/STSC/STSCvenv/UI/LIVE/PI", "PILIVE") #take image
    
            #display image
            test_image = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/PI/PILIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=test_image, size=(470, 315))
            label = ctk.CTkLabel(live_loop_frame, text="", image=Z_live_test)
            label.place(x=100, y=380) 
            time.sleep(exptime)
        time.sleep(1)

def stopLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 0
    print("ZWOLiveActive --> " + str(ZWOLiveActive))

def startLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 1
    print("Main Camera Looping Exposure Enabled")
  
def stopLivePIImage():
    global PILiveActive
    PILiveActive = 0
    print("PILiveActive --> " + str(PILiveActive))

def startLivePIImage():
    global PILiveActive
    PILiveActive = 1
    print("Guide Camera Looping Exposure Enabled")

#open phd2 [UPDATE TO CLOSE PI CONNECTION PRIOR TO OPENING]
def open_phd2():
    print("Disconnecting Guide Camera")
    iface.setSwitch(PIcam, "CONNECTION", "DISCONNECT", "On")
    iface.sendProperty(PIcam, "CONNECTION")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("Opening PHD2...")

#takes and saves a picture on the ZWO camera
def takeZWOPicture(exp_time, save_location, upload_prefix):
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", save_location)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", upload_prefix)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
    iface.setNumber(ZWOcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", float(exp_time))
    iface.sendProperty(ZWOcam, "CCD_EXPOSURE")

    #wait until exposure is done
    ccdState = "Busy"
    while True:
        ccdState = iface.getPropertyState(ZWOcam, "CCD_EXPOSURE")
        if (ccdState != "Ok"):
            time.sleep(1)
        else:
            break
    
#takes and saves a picture on the ZWO camera
def takePIPicture(exp_time, save_location, upload_prefix):
    print(f"Taking a CCD exposure on the PI camera...")
    iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", save_location)
    iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
    iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", upload_prefix)
    iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
    iface.setNumber(PIcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", float(exp_time))
    iface.sendProperty(PIcam, "CCD_EXPOSURE")

    #wait until exposure is done
    ccdState = "Busy"
    while True:
        ccdState = iface.getPropertyState(PIcam, "CCD_EXPOSURE")
        if (ccdState != "Ok"):
            time.sleep(1)
        else:
            break
    print("Image captured from PI Camera.")

#submit the ZWO settings to the INDI server
def submitZWOsettings():
    gain = ZWOgain_text.get("1.0", "end-1c")
    exposure_time = float(ZWOexposure_time_text.get("1.0", "end-1c").strip())
    temperature = ZWOtemperature_text.get("1.0", "end-1c")

    if not gain.strip():  #check if the content is empty or contains only whitespace
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
            #set gain
            iface.setNumber(ZWOcam, "CCD_CONTROLS", "Gain", gain_value)
            iface.sendProperty(ZWOcam, "CCD_CONTROLS")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"Gain is set at {gain_value}")

    if not exposure_time.strip():  #check if the content is empty or contains only whitespace
        exposure_time_value = 1
    else:
        try:
            exposure_time_value = int(exposure_time)
            iface.setNumber(ZWOcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", exposure_time_value)
            #iface.sendProperty(ZWOcam, "CCD_EXPOSURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"Exposure time is set at {exposure_time_value} seconds")
    
    if not temperature.strip():  #check if the content is empty or contains only whitespace
        temperature_value = 0
    else:
        try:
            temperature_value = int(temperature)
            iface.setNumber(ZWOcam, "CCD_TEMPERATURE", "CCD_TEMPERATURE_VALUE", temperature_value)
            iface.sendProperty(ZWOcam, "CCD_TEMPERATURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid temperature")
            return
    print(f"Temperature is set at {temperature_value} Â°C")

#submit the PI settings to the INDI server
def submitPIsettings():
    gain = PIgain_text.get("1.0", "end-1c")
    exposure_time = PIexposure_time_text.get("1.0", "end-1c")

    if not gain.strip():  #check if the content is empty or contains only whitespace
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
            #set gain
            iface.setNumber(PIcam, "CCD_GAIN", "GAIN", gain_value)
            iface.sendProperty(PIcam, "CCD_GAIN")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"Gain is set at {gain_value}")

    if not exposure_time.strip():  #check if the content is empty or contains only whitespace
        exposure_time_value = 1
    else:
        try:
            exposure_time_value = int(exposure_time)
            iface.setNumber(PIcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", exposure_time_value)
            #iface.sendProperty(ZWOcam, "CCD_EXPOSURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"Exposure time is set at {exposure_time_value} seconds")

#move the mount north
def moveNorth():
    print("Mount moved north")

#move the mount south
def moveSouth():
    print("Mount moved south")

#move the mount east
def moveEast():
    print("Mount moved east")

#move the mount west
def moveWest():
    print("Mount moved west")

#terminate UI
def close():
    root.destroy()

#----- START INITIALIZE DEVICES -----
ZWOcam = "ZWO CCD ASI294MC Pro"
PIcam = "indi_pylibcamera"
Mount = "Celestron GPS"

#starts daemon ZWO and PI livestream threads for live capture
ZWOLiveActive = 0
ZWOLiveThread = threading.Thread(target=ZWOLiveThreadFunc)
ZWOLiveThread.daemon = True #kills on program exit
PILiveActive = 0
PILiveThread = threading.Thread(target=PILiveThreadFunc)
PILiveThread.daemon = True #kills on program exit

ZWOLiveThread.start()
print("ZWOLiveThread has started")
PILiveThread.start()
print("PILiveThread has started")

gobject.threads_init()
glib.init_threads()

#Create a session bus.
bus = dbus.SessionBus()

# Create an object that will proxy for a particular remote object.
remote_object = bus.get_object("org.kde.kstars", "/KStars/INDI")

# Introspection returns an XML document containing information
# about the methods supported by an interface.
#print("Introspection data:\n")
#print(remote_object.Introspect())

# Get INDI interface
iface = dbus.Interface(remote_object, 'org.kde.kstars.INDI')

# Start INDI devices
while not iface.connect("localhost", 7624):
    time.sleep(1)

print("Waiting for INDI devices...")

# Create array for received devices
devices = []

while True:
    devices = iface.getDevices()
    if (len(devices) < 3):
        time.sleep(1)
    else:
        break

print("We received the following devices:")
for device in devices:
    print(device)

#connect to drivers
iface.setSwitch(ZWOcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(ZWOcam, "CONNECTION")
iface.setSwitch(PIcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(PIcam, "CONNECTION")
iface.setSwitch(Mount, "CONNECTION", "CONNECT", "On")
iface.sendProperty(Mount, "CONNECTION")
ccdState = "Busy"

while True:
    ccdState = iface.getPropertyState(ZWOcam, "CONNECTION")
    if (ccdState != "Ok"):
        time.sleep(1)
    else:
        break

print("Connection to Telescope and CCD is established.")

#prints out all properties of each device
'''
ZWOProps = iface.getProperties(ZWOcam)
PIProps = iface.getProperties(PIcam)
MOUNTProps = iface.getProperties(Mount)
print(f"\nvvv ZWO PROPERTIES vvv")
for ZWOProp in ZWOProps:
    print(ZWOProp)
    
print(f"\nvvv PI PROPERTIES vvv")
for PIProp in PIProps:
    print(PIProp)
    
print(f"\nvvv MOUNT PROPERTIES vvv")
for MountProp in MOUNTProps:
    print(MountProp)
'''

#set cooling & temp in ZWO camera
iface.setSwitch(ZWOcam, "CCD_COOLER", "COOLER_ON", "On")
iface.sendProperty(ZWOcam, "CCD_COOLER")

iface.setText(ZWOcam, "CCD_TEMPERATURE", "CCD_TEMPERATURE_VALUE", "13.00")
iface.sendProperty(ZWOcam, "CCD_TEMPERATURE")

#set up images for local storage
iface.setSwitch(ZWOcam, "UPLOAD_MODE", "UPLOAD_LOCAL", "On")
iface.sendProperty(ZWOcam, "UPLOAD_MODE")
iface.setSwitch(PIcam, "UPLOAD_MODE", "UPLOAD_LOCAL", "On")
iface.sendProperty(PIcam, "UPLOAD_MODE")
 
#set location of images
iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures")
iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", "/home/starspec/STSC/STSCvenv/UI/PICaptures")
iface.sendProperty(PIcam, "UPLOAD_SETTINGS")

#set name of images
iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", "ZWO_IMAGE_XXX")
iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", "PI_IMAGE_XXX")
iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
#----- END INITIALIZE DEVICES -----

#----- START INITIALIZE GUI -----
#system appearance
ctk.set_appearance_mode("System")

#frame
root = ctk.CTk()
root.minsize(420, 360)
root.maxsize(840, 720)
root.geometry("840x720+440+55")
root.title("StarSpec UI")

#define background
image = Image.open("Space_Image.jpeg")
bg = ctk.CTkImage(dark_image=image, size=(840, 720))

#create 1st frame (live loop)
live_loop_frame = ctk.CTkFrame(root)
live_loop_frame.pack(fill="both", expand=1)
bg_image1 = ctk.CTkLabel(live_loop_frame, image=bg, text="")
bg_image1.pack(expand=1)
bg_image1.place(x=0, y=0)

#create 2nd frame (capture settings)
capture_settings_frame = ctk.CTkFrame(root)
capture_settings_frame.pack(fill="both", expand=1)
capture_settings_frame.place(x=0, y=0)
bg_image2 = ctk.CTkLabel(capture_settings_frame, image=bg, text="")
bg_image2.pack(expand=1)

#create 3rd frame (loop settings)
loop_settings_frame = ctk.CTkFrame(root)
loop_settings_frame.pack(fill="both", expand=1)
loop_settings_frame.place(x=0, y=0)
bg_image3 = ctk.CTkLabel(loop_settings_frame, image=bg, text="")
bg_image3.pack(expand=1)
#----- END INITIALIZE GUI -----

#----- START LIVE LOOP BUTTONS -----
live_view = ctk.CTkButton(live_loop_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_loop_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=10, y=10)

loop_settings = ctk.CTkButton(live_loop_frame,
                                text="Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:loop_settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=116, y=10)

capture_settings = ctk.CTkButton(live_loop_frame,
                                text="Capture", font=("Helvetica", 18), text_color="white",
                                command=lambda:capture_settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=190, y=10)

north = ctk.CTkButton(live_loop_frame,
                        text="N", font=("Helvetica", 16), text_color="white",
                        command=moveNorth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#3f2930", "black", "#141b1c", "#2d2d34"))
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=730, y=294)

south = ctk.CTkButton(live_loop_frame,
                        text="S", font=("Helvetica", 16), text_color="white",
                        command=moveSouth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=730, y=394)

east = ctk.CTkButton(live_loop_frame,
                        text="E", font=("Helvetica", 16), text_color="white",
                        command=moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=780, y=344)

west = ctk.CTkButton(live_loop_frame,
                        text="W", font=("Helvetica", 16), text_color="white",
                        command=moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "#624146", "#703d41", "black"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=680, y=344)

start_Z_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:startLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_Z_liveloop.pack(anchor="nw", expand=1)
start_Z_liveloop.place(x=610, y=180)

stop_Z_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:stopLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_Z_liveloop.pack(anchor="nw", expand=1)
stop_Z_liveloop.place(x=610, y=220)

start_PI_liveloop = ctk.CTkButton(live_loop_frame,
                                    text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:startLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_PI_liveloop.pack(anchor="nw", expand=1)
start_PI_liveloop.place(x=610, y=520)

stop_PI_liveloop = ctk.CTkButton(live_loop_frame,
                                    text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:stopLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_PI_liveloop.pack(anchor="nw", expand=1)
stop_PI_liveloop.place(x=610, y=560)

close_button1 = ctk.CTkButton(live_loop_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button1.pack(anchor="nw", expand=1)
close_button1.place(x=760, y=680)
#----- END LIVE LOOP BUTTONS -----

#----- START LOOP SETTINGS BUTTONS -----
live_view = ctk.CTkButton(loop_settings_frame,
                        text="Live View", font=("Helvetica", 18), text_color="white",
                        command=lambda:live_loop_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=10, y=10)

loop_settings = ctk.CTkButton(loop_settings_frame,
                                text="Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:loop_settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=116, y=10)

capture_settings = ctk.CTkButton(loop_settings_frame,
                            text="Capture", font=("Helvetica", 18), text_color="white",
                            command=lambda:capture_settings_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=190, y=10)

ZWOsubmit_button = ctk.CTkButton(loop_settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitZWOsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
ZWOsubmit_button.pack(anchor="nw", expand=1)
ZWOsubmit_button.place(x=100, y=260)

PIsubmit_button = ctk.CTkButton(loop_settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitPIsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
PIsubmit_button.pack(padx=10, pady=10, anchor="nw", expand=1)
PIsubmit_button.place(x=350, y=260)

close_button2 = ctk.CTkButton(loop_settings_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button2.pack(anchor="nw", expand=1)
close_button2.place(x=760, y=680)

#ZWO Camera Settings
ZWOtitle_label = ctk.CTkLabel(loop_settings_frame,
                                text="MAIN SETTINGS", font=("Helvetica", 18), text_color="white",
                                fg_color="black",  bg_color="black",
                                corner_radius=10)
ZWOtitle_label.pack(anchor="nw", expand=1)
ZWOtitle_label.place(x=50, y=60)

#set ZWO gain
ZWOgain_label = ctk.CTkLabel(loop_settings_frame,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
ZWOgain_label.pack(anchor="nw", expand=1)
ZWOgain_label.place(x=10, y=105)

ZWOgain_text = ctk.CTkTextbox(loop_settings_frame,
                                font=("Helvetica", 18),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False" )
ZWOgain_text.pack(anchor="nw", expand=1)
ZWOgain_text.place(x=180, y=100)

#set ZWO exposure time
ZWOexposure_time_label = ctk.CTkLabel(loop_settings_frame,
                                        text="Exposure Time(s):", font=("Helvetica", 18), text_color="white",
                                        fg_color="black",  bg_color="black",
                                        corner_radius=10)
ZWOexposure_time_label.pack(anchor="nw", expand=1)
ZWOexposure_time_label.place(x=10, y=155)

ZWOexposure_time_text = ctk.CTkTextbox(loop_settings_frame,
                                        font=("Helvetica", 18),
                                        fg_color="white", bg_color="black", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
ZWOexposure_time_text.pack(anchor="nw", expand=1)
ZWOexposure_time_text.place(x=180, y=150)

#set ZWO temperature
ZWOtemperature_label = ctk.CTkLabel(loop_settings_frame,
                                    text="Temperature(°C):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    corner_radius=10)
ZWOtemperature_label.pack(anchor="nw", expand=1)
ZWOtemperature_label.place(x=10, y=205)

ZWOtemperature_text = ctk.CTkTextbox(loop_settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=70,
                                    activate_scrollbars="False")
ZWOtemperature_text.pack(anchor="nw", expand=1)
ZWOtemperature_text.place(x=180, y=200)

PItitle_label = ctk.CTkLabel(loop_settings_frame,
                            text="GUIDE SETTINGS", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
PItitle_label.pack(anchor="nw", expand=1)
PItitle_label.place(x=300, y=60)

#set PI gain
PIgain_label = ctk.CTkLabel(loop_settings_frame,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
PIgain_label.pack(anchor="nw", expand=1)
PIgain_label.place(x=270, y=105)

PIgain_text = ctk.CTkTextbox(loop_settings_frame,
                                font=("Helvetica", 18),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False")
PIgain_text.pack(anchor="nw", expand=1)
PIgain_text.place(x=440, y=100)

#set PI exposure time
PIexposure_time_label = ctk.CTkLabel(loop_settings_frame,
                                        text="Exposure Time(s):", font=("Helvetica", 18), text_color="white",
                                        fg_color="black",  bg_color="black",
                                        corner_radius=10)
PIexposure_time_label.pack(anchor="nw", expand=1)
PIexposure_time_label.place(x=270, y=155)

PIexposure_time_text = ctk.CTkTextbox(loop_settings_frame,
                                        font=("Helvetica", 18),
                                        fg_color="white", bg_color="black", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
PIexposure_time_text.pack(anchor="nw", expand=1)
PIexposure_time_text.place(x=440, y=150)
#----- END LOOP SETTINGS BUTTONS -----

#----- START CAPTURE SETTINGS BUTTONS -----
live_view = ctk.CTkButton(capture_settings_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_loop_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=10, y=10)

loop_settings = ctk.CTkButton(capture_settings_frame,
                                text="Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:loop_settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=116, y=10)

capture_settings = ctk.CTkButton(capture_settings_frame,
                                text="Capture", font=("Helvetica", 18), text_color="white",
                                command=lambda:capture_settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=190, y=10)

phd2_button = ctk.CTkButton(capture_settings_frame,
                            text="Open PHD2", font=("Helvetica", 18), text_color="white",
                            command=lambda:open_phd2,
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
phd2_button.pack(expand=1)
phd2_button.place(x=715, y=10)

capture_ZWO_image = ctk.CTkButton(capture_settings_frame,
                                    text="Capture ZWO Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takeZWOPicture(int(exposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures", "ZWO_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_ZWO_image.pack(anchor="nw", expand=1)
capture_ZWO_image.place(x=230, y=680)

capture_PI_image = ctk.CTkButton(capture_settings_frame,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(int(exposure_time_text.get("1.0", "end-1c"))),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_PI_image.pack(anchor="nw", expand=1)
capture_PI_image.place(x=420, y=680)

close_button3 = ctk.CTkButton(capture_settings_frame,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button3.pack(anchor="nw", expand=1)
close_button3.place(x=760, y=680)
#----- END CAPTURE SETTINGS BUTTONS -----

live_loop_frame.tkraise() #start the UI on the live loop frame

#Run UI
root.mainloop()
