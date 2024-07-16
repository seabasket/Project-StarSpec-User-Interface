import subprocess
import time

import os
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
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"Gain is set at {gain_value}")

    if not exposure_time.strip():  #check if the content is empty or contains only whitespace
        exposure_time_value = 1
    else:
        try:
            exposure_time_value = int(exposure_time)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"Exposure time is set at {exposure_time_value} seconds")
    
    if not temperature.strip():  #check if the content is empty or contains only whitespace
        temperature_value = 0
    else:
        try:
            temperature_value = int(temperature)
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

west = ctk.CTkButton(live_loop_frame,
                        text="W", font=("Helvetica", 16), text_color="white",
                        command=moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "#624146", "#703d41", "black"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=680, y=344)

east = ctk.CTkButton(live_loop_frame,
                        text="E", font=("Helvetica", 16), text_color="white",
                        command=moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=780, y=344)

test_image = Image.open("JT.jpg")
jt = ctk.CTkImage(dark_image=test_image, size=(470, 315))

label = ctk.CTkLabel(live_loop_frame, width=470, height=315, text="")
label.pack()
label.place(x=100, y=60)

label2 = ctk.CTkLabel(live_loop_frame, width=470, height=315, text="")
label2.pack()
label2.place(x=100, y=380)

start_Z_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                command=captureZ_live,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_Z_liveloop.pack(anchor="nw", expand=1)
start_Z_liveloop.place(x=610, y=180)

start_PI_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                command=captureZ_live,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_PI_liveloop.pack(anchor="nw", expand=1)
start_PI_liveloop.place(x=610, y=520)

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

submit_button = ctk.CTkButton(loop_settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitZWOsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
submit_button.pack(padx=10, pady=10, anchor="nw", expand=1)
submit_button.place(x=60, y=180)

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
gain_label.place(x=10, y=50)

gain_text = ctk.CTkTextbox(loop_settings_frame,
                            font=("Helvetica", 18),
                            fg_color="white", bg_color="black", text_color="black",
                            height=20, width=70,
                            activate_scrollbars="False"
                            )
gain_text.pack(anchor="nw", expand=1)
gain_text.place(x=180, y=50)

#set ZWO exposure time
exposure_time_label = ctk.CTkLabel(loop_settings_frame,
                                    text="Exposure Time (s):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    corner_radius=10)
exposure_time_label.pack(anchor="nw", expand=1)
exposure_time_label.place(x=10, y=90)

exposure_time_text = ctk.CTkTextbox(loop_settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=70,
                                    activate_scrollbars="False"
                                    )
exposure_time_text.pack(anchor="nw", expand=1)
exposure_time_text.place(x=180, y=90)

#set ZWO temperature
temperature_label = ctk.CTkLabel(loop_settings_frame,
                                    text="Temperature (°C):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    corner_radius=10)
temperature_label.pack(anchor="nw", expand=1)
temperature_label.place(x=10, y=130)

temperature_text = ctk.CTkTextbox(loop_settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=70,
                                    activate_scrollbars="False"
                                    )
temperature_text.pack(anchor="nw", expand=1)
temperature_text.place(x=180, y=130)
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
capture_ZWO_image.pack(padx=10, pady=10, anchor="nw", expand=1)
capture_ZWO_image.place(x=230, y=680)

capture_PI_image = ctk.CTkButton(capture_settings_frame,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(int(exposure_time_text.get("1.0", "end-1c"))),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    height=30, width=80,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_PI_image.pack(padx=10, pady=10, anchor="nw", expand=1)
capture_PI_image.place(x=420, y=680)

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
