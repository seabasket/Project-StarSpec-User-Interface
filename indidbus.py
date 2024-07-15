import subprocess
import time
#run KSTARS_init.sh to init INDI server
KSTARS_init_path = "./KSTARS_init.sh"
KSTARS_init_command = f"gnome-terminal -- bash -c '{KSTARS_init_path}; exec bash'"
KSTARS_init_process = subprocess.Popen(KSTARS_init_command, shell=True)
time.sleep(3)

#run INDI_init.sh to init INDI server
INDI_init_path = "./INDI_init.sh"
INDI_init_command = f"gnome-terminal -- bash -c '{INDI_init_path}; exec bash'"
INDI_init_process = subprocess.Popen(INDI_init_command, shell=True)
time.sleep(3)

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

#start PHD2 and INDI Server

ZWOcam = "ZWO CCD ASI294MC Pro"
PIcam = "indi_pylibcamera"

gobject.threads_init()

from dbus import glib
glib.init_threads()

#Create a session bus.
import dbus
bus = dbus.SessionBus()

# Create an object that will proxy for a particular remote object.
remote_object = bus.get_object("org.kde.kstars", # Connection name
                               "/KStars/INDI" # Object's path
                              )

# Introspection returns an XML document containing information
# about the methods supported by an interface.
print("Introspection data:\n")
print(remote_object.Introspect())

# Get INDI interface
iface = dbus.Interface(remote_object, 'org.kde.kstars.INDI')

myDevices = ["indi_asi_ccd"]

# Start INDI devices
while not iface.connect("localhost", 7624):
    time.sleep(1)

print("Waiting for INDI devices...")

# Create array for received devices
devices = []

while True:
    devices = iface.getDevices()
    if (len(devices) < len(myDevices)):
        time.sleep(1)
    else:
        break;

print("We received the following devices:")
for device in devices:
    print(device)

#connect to cameras
iface.setSwitch(ZWOcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(ZWOcam, "CONNECTION")
iface.setSwitch(PIcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(PIcam, "CONNECTION")
ccdState = "Busy"

while True:
    ccdState = iface.getPropertyState(ZWOcam, "CONNECTION")
    if (ccdState != "Ok"):
        time.sleep(1)
    else:
        break

print("Connection to Telescope and CCD is established.")

#set cooling & temp in ZWO camera
iface.setSwitch(ZWOcam, "CCD_COOLER", "COOLER_ON", "On")
iface.sendProperty(ZWOcam, "CCD_COOLER")

iface.setText(ZWOcam, "CCD_TEMPERATURE", "CCD_TEMPERATURE_VALUE", "13.00")
iface.sendProperty(ZWOcam, "CCD_TEMPERATURE")

#set gain
iface.setText(ZWOcam, "CCD_CONTROLS", "Gain", "250.000")
iface.sendProperty(ZWOcam, "CCD_CONTROLS")

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

def takeZWOPicture(exp_time):
    print(f"Taking a {exp_time} second CCD exposure on the ZWO camera...")
    iface.setNumber(ZWOcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", exp_time)
    iface.sendProperty(ZWOcam, "CCD_EXPOSURE")
    #wait until exposure is done
    ccdState = "Busy"
    while True:
        ccdState = iface.getPropertyState(ZWOcam, "CCD_EXPOSURE")
        if (ccdState != "Ok"):
            time.sleep(1)
        else:
            break
    print("Image captured from ZWO Camera.")

def takePIPicture(exp_time):
    print(f"Taking a {exp_time} second CCD exposure on the PI camera...")
    iface.setNumber(PIcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", exp_time)
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

#create 1st frame (main controls)
frame1 = ctk.CTkFrame(root)
frame1.pack(fill="both", expand=1)
bg_image1 = ctk.CTkLabel(frame1, image=bg, text="")
bg_image1.pack(expand=1)
bg_image1.place(x=0, y=0)

#create 2nd frame (mount controls/live view)
frame2 = ctk.CTkFrame(root)
frame2.pack(fill="both", expand=1)
frame2.place(x=0, y=0)
bg_image2 = ctk.CTkLabel(frame2, image=bg, text="")
bg_image2.pack(expand=1)

#terminate code feature
def close():
    root.destroy()

#set gain
gain_label = ctk.CTkLabel(frame1,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            height=30, width=50,
                            corner_radius=10)
gain_label.pack(anchor="nw", expand=1)
gain_label.place(x=10, y=10)

gain_text = ctk.CTkTextbox(frame1,
                            font=("Helvetica", 18),
                            fg_color="white", bg_color="black", text_color="black",
                            height=30, width=50
                            )
gain_text.pack(padx=10, pady=10, anchor="nw", expand=1)
gain_text.place(x=65, y=10)

#set exposure time
exposure_time_label = ctk.CTkLabel(frame1,
                                    text="Exposure Time:", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    height=30, width=50,
                                    corner_radius=10)
exposure_time_label.pack(anchor="nw", expand=1)
exposure_time_label.place(x=10, y=60)

exposure_time_text = ctk.CTkTextbox(frame1,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=30, width=50
                                    )
exposure_time_text.pack(padx=10, pady=10, anchor="nw", expand=1)
exposure_time_text.place(x=150, y=60)  

def submit():
    gain = gain_text.get("1.0", "end-1c")
    exposure_time = exposure_time_text.get("1.0", "end-1c")

    if not gain.strip():  #check if the content is empty or contains only whitespace
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"Gain is set at {gain_value}")

    if not exposure_time.strip():  #check if the content is empty or contains only whitespace
        exposure_time_value = 0
    else:
        try:
            exposure_time_value = int(exposure_time)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"Exposure time is set at {exposure_time_value} seconds")

submit_button = ctk.CTkButton(frame1,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submit,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
submit_button.pack(padx=10, pady=10, anchor="nw", expand=1)
submit_button.place(x=200, y=100)
        
first_close_button = ctk.CTkButton(frame1,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
first_close_button.pack(padx=10, pady=10, anchor="nw", expand=1)
first_close_button.place(x=770, y=680)

second_close_button = ctk.CTkButton(frame2,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
second_close_button.pack(padx=10, pady=10, anchor="nw", expand=1)
second_close_button.place(x=770, y=680)

def open_phd2():
    print("PHD2 is open.")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("output: ", stdout)
    print("error: ", stderr)

#PHD2 button
phd2_button = ctk.CTkButton(frame1,
                            text="Open PHD2", font=("Helvetica", 18), text_color="white",
                            command=lambda:open_phd2,
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
phd2_button.pack(expand=1)
phd2_button.place(x=600, y=10)

#buttons that will switch between pages
switch1 = ctk.CTkButton(frame1,
                        text="Live View", font=("Helvetica", 18), text_color="white",
                        command=lambda:frame2.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
switch1.pack(expand=1)
switch1.place(x=730, y=10)

switch2 = ctk.CTkButton(frame2,
                        text="Main Control", font=("Helvetica", 18), text_color="white",
                        command=lambda:frame1.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
switch2.pack(expand=1)
switch2.place(x=710, y=10)

#mount control feature
def moveNorth():
    print("Mount moved north")
def moveSouth():
    print("Mount moved south")
def moveWest():
    print("Mount moved west")
def moveEast():
    print("Mount moved east")

north = ctk.CTkButton(frame2,
                        text="N", font=("Helvetica", 18), text_color="white",
                        command=lambda:moveNorth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=730, y=50)

south = ctk.CTkButton(frame2,
                        text="S", font=("Helvetica", 18), text_color="white",
                        command=lambda:moveSouth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=730, y=150)

west = ctk.CTkButton(frame2,
                        text="W", font=("Helvetica", 18), text_color="white",
                        command=lambda:moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=680, y=100)

east = ctk.CTkButton(frame2,
                        text="E", font=("Helvetica", 18), text_color="white",
                        command=lambda:moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=780, y=100)

caputure_ZWO_image = ctk.CTkButton(frame2,
                                    text="Capture ZWO Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takeZWOPicture(5),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
caputure_ZWO_image.pack(padx=10, pady=10, anchor="nw", expand=1)
caputure_ZWO_image.place(x=420, y=680)

caputure_PI_image = ctk.CTkButton(frame2,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(5),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
caputure_PI_image.pack(padx=10, pady=10, anchor="nw", expand=1)
caputure_PI_image.place(x=260, y=680)

frame1.tkraise()
#Run app
root.mainloop()
