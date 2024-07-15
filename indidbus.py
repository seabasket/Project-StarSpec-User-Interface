import subprocess
import time

#run KSTARS_init.sh to initialize INDI server
KSTARS_init_path = "./KSTARS_init.sh"
KSTARS_init_command = f"gnome-terminal -- bash -c '{KSTARS_init_path}; exec bash'"
KSTARS_init_process = subprocess.Popen(KSTARS_init_command, shell=True)
time.sleep(6)

#run INDI_init.sh to initizlize INDI server
INDI_init_path = "./INDI_init.sh"
INDI_init_command = f"gnome-terminal -- bash -c '{INDI_init_path}; exec bash'"
INDI_init_process = subprocess.Popen(INDI_init_command, shell=True)
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

def captureZ_live():
    #get exposure time for image capture
    try:
        exptime = int(exposure_time_text.get("1.0", "end-1c"))
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
        exptime = 1
        return

#open phd2 [UPDATE TO CLOSE PI CONNECTION PRIOR TO OPENING]
def open_phd2():
    print("PHD2 is open.")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("output: ", stdout)
    print("error: ", stderr)

#takes and saves a picture on the ZWO camera
def takeZWOPicture(exp_time, save_location, upload_prefix):
    print(f"Taking a CCD exposure on the ZWO camera...")
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", save_location)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", upload_prefix)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
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

#[UPDATE]takes and saves a picture on the PIP camera
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

#submit the ZWO settings to the INDI server
def submitZWOsettings():
    gain = gain_text.get("1.0", "end-1c")
    exposure_time = exposure_time_text.get("1.0", "end-1c")
    temperature = temperature_text.get("1.0", "end-1c")

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
    print(f"Temperature is set at {temperature_value} °C")

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
Mount = "Celestron NexStar HC"

gobject.threads_init()
glib.init_threads()

#Create a session bus.
bus = dbus.SessionBus()

# Create an object that will proxy for a particular remote object.
remote_object = bus.get_object("org.kde.kstars", "/KStars/INDI")

# Introspection returns an XML document containing information
# about the methods supported by an interface.
print("Introspection data:\n")
print(remote_object.Introspect())

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
live_view.place(x=20, y=680)

loop_settings = ctk.CTkButton(live_loop_frame,
                        text="Loop", font=("Helvetica", 18), text_color="white",
                        command=lambda:loop_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=120, y=680)

capture_settings = ctk.CTkButton(live_loop_frame,
                        text="Capture", font=("Helvetica", 18), text_color="white",
                        command=lambda:capture_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=220, y=680)

north = ctk.CTkButton(live_loop_frame,
                        text="N", font=("Helvetica", 18), text_color="white",
                        command=moveNorth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=730, y=250)

south = ctk.CTkButton(live_loop_frame,
                        text="S", font=("Helvetica", 18), text_color="white",
                        command=moveSouth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=730, y=350)

west = ctk.CTkButton(live_loop_frame,
                        text="W", font=("Helvetica", 18), text_color="white",
                        command=moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=680, y=300)

east = ctk.CTkButton(live_loop_frame,
                        text="E", font=("Helvetica", 18), text_color="white",
                        command=moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=780, y=300)

start_Z_liveloop = ctk.CTkButton(live_loop_frame,
                        text="Start Z Live Loop", font=("Helvetica", 18), text_color="white",
                        command=captureZ_live,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=40, width=40,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_Z_liveloop.pack(anchor="nw", expand=1)
start_Z_liveloop.place(x=650, y=100)

close_button1 = ctk.CTkButton(live_loop_frame,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button1.pack(padx=10, pady=10, anchor="nw", expand=1)
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
live_view.place(x=20, y=680)

loop_settings = ctk.CTkButton(loop_settings_frame,
                        text="Loop", font=("Helvetica", 18), text_color="white",
                        command=lambda:loop_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=120, y=680)

capture_settings = ctk.CTkButton(loop_settings_frame,
                        text="Capture", font=("Helvetica", 18), text_color="white",
                        command=lambda:capture_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=220, y=680)

submit_button = ctk.CTkButton(loop_settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitZWOsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
submit_button.pack(padx=10, pady=10, anchor="nw", expand=1)
submit_button.place(x=50, y=120)

close_button2 = ctk.CTkButton(loop_settings_frame,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button2.pack(padx=10, pady=10, anchor="nw", expand=1)
close_button2.place(x=760, y=680)

#set ZWO gain
gain_label = ctk.CTkLabel(loop_settings_frame,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
gain_label.pack(anchor="nw", expand=1)
gain_label.place(x=10, y=15)

gain_text = ctk.CTkTextbox(loop_settings_frame,
                            font=("Helvetica", 18),
                            fg_color="white", bg_color="black", text_color="black",
                            height=20, width=50,
                            activate_scrollbars="False"
                            )
gain_text.pack(anchor="nw", expand=1)
gain_text.place(x=180, y=10)

#set ZWO exposure time
exposure_time_label = ctk.CTkLabel(loop_settings_frame,
                                    text="Exposure Time (s):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    height=30, width=50,
                                    corner_radius=10)
exposure_time_label.pack(anchor="nw", expand=1)
exposure_time_label.place(x=10, y=45)

exposure_time_text = ctk.CTkTextbox(loop_settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=50,
                                    activate_scrollbars="False"
                                    )
exposure_time_text.pack(anchor="nw", expand=1)
exposure_time_text.place(x=180, y=50)

#set ZWO temperature
temperature_label = ctk.CTkLabel(loop_settings_frame,
                                    text="Temperature (Â°C):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    height=30, width=50,
                                    corner_radius=10)
temperature_label.pack(anchor="nw", expand=1)
temperature_label.place(x=10, y=75)

temperature_text = ctk.CTkTextbox(loop_settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=50,
                                    activate_scrollbars="False"
                                    )
temperature_text.pack(anchor="nw", expand=1)
temperature_text.place(x=180, y=90)
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
live_view.place(x=20, y=680)

loop_settings = ctk.CTkButton(capture_settings_frame,
                        text="Loop", font=("Helvetica", 18), text_color="white",
                        command=lambda:loop_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=120, y=680)

capture_settings = ctk.CTkButton(capture_settings_frame,
                        text="Capture", font=("Helvetica", 18), text_color="white",
                        command=lambda:capture_settings_frame.tkraise(),
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
capture_settings.pack(expand=1)
capture_settings.place(x=220, y=680)

phd2_button = ctk.CTkButton(capture_settings_frame,
                            text="Open PHD2", font=("Helvetica", 18), text_color="white",
                            command=lambda:open_phd2,
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
phd2_button.pack(expand=1)
phd2_button.place(x=710, y=10)

capture_ZWO_image = ctk.CTkButton(capture_settings_frame,
                                    text="Capture ZWO Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takeZWOPicture(int(exposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures", "ZWO_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_ZWO_image.pack(padx=10, pady=10, anchor="nw", expand=1)
capture_ZWO_image.place(x=520, y=680)

capture_PI_image = ctk.CTkButton(capture_settings_frame,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(int(exposure_time_text.get("1.0", "end-1c"))),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_PI_image.pack(padx=10, pady=10, anchor="nw", expand=1)
capture_PI_image.place(x=360, y=680)

close_button3 = ctk.CTkButton(capture_settings_frame,
                                    text="Close", font=("Helvetica", 18), text_color="white",
                                    command=close,
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=60,
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button3.pack(padx=10, pady=10, anchor="nw", expand=1)
close_button3.place(x=760, y=680)
#----- END CAPTURE SETTINGS BUTTONS -----

live_loop_frame.tkraise() #start the UI on the live loop frame

#Run UI
root.mainloop()
