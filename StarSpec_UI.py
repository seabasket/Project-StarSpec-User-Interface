import subprocess
import PyIndi
import time
#run INDI_init.sh to init INDI server
INDI_init_path = "./INDI_init.sh"
INDI_init_command = f"gnome-terminal -- bash -c '{INDI_init_path}; exec bash'"
INDI_init_process = subprocess.Popen(INDI_init_command, shell=True) 

import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
import customtkinter as ctk
from PIL import ImageTk, Image
import cv2
from cv2 import *

#Indi Client Setup
class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.zcamera = "ZWO CCD"
        self.picamera = "indi_pylibcamera"
        self.device = None
    def newDevice(self, d):
        if d.getDeviceName() == self.zcamera:
                self.device = d
        if d.getDeviceName() == self.picamera:
                self.device = d
    def newProperty(self, p):
        global monitored, cmonitor
        if(p.getDeviceName() == "ZWO CCD" and p.getName() == "CONNECTION"):
                cmonitor = p.getSwitch()
        print(f"New property: {p.getName()} for device {p.getDeviceName()}")
        
        if(p.getDeviceName() == "indi_pylibcamera" and p.getName() == "CONNECTION"):
                cmonitor = p.getSwitch()
        print(f"New property: {p.getName()} for device {p.getDeviceName()}")
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        print(f"New message from {d.getDeviceName()}: {m.message}")
    def serverConnected(self):
        print("Server connected.")
    def serverDisconnected(self, code):
        print(f"Server disconnected (code {code})")
        passent.sendNewSwitch(cmonitor) # send this new value to the device

#initialization of INDI server
indiclient=IndiClient()
indiclient.setServer("localhost",7624)
for i in range(30):
        if indiclient.device:
                break
        if i == 1:
                print("Waiting for devices & properties...")
        time.sleep(1)

if not indiclient.connectServer():
        print("INDI server failed to connect.")
        exit(1)
if not indiclient.device is None:
        print("Device not found.")
else:
        print("Device is connected!")

#system appearance
ctk.set_appearance_mode("System")

#frame
root = ctk.CTk()
root.minsize(420, 360)
root.maxsize(840, 720)
root.geometry("840x720+440+55")
root.title("StarSpec UI")

#define background
image = Image.open("Space_Image.jpg")
bg = ImageTk.PhotoImage(image)

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
def terminate():
        root.destroy()
        
terminate_button = ctk.CTkButton(frame1,
                text="Terminate", font=("Helvetica", 18), text_color="white",
                command=terminate,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=30, width=80,
                border_color="white", border_width=2, background_corner_colors=("#653646", "#515062", "#4c3e55", "#b96074"))
terminate_button.pack(padx=10, pady=10, anchor="nw", expand=1)
terminate_button.place(x=356, y=680)

def open_phd2():
    print("PHD2 is open.")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("output: ", stdout)
    print("error: ", stderr)
    

#PHD2 button
phd2_button = ctk.CTkButton(frame1,
                        text="Open PHD2", font=("Helvetica", 18), text_color="white",
                        command=open_phd2,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
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
                        border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
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
                command=moveNorth,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=40, width=40,
                corner_radius=10,
                border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=730, y=50)

south = ctk.CTkButton(frame2,
                text="S", font=("Helvetica", 18), text_color="white",
                command=moveSouth,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=40, width=40,
                corner_radius=10,
                border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=730, y=150)

west = ctk.CTkButton(frame2,
                text="W", font=("Helvetica", 18), text_color="white",
                command=moveWest,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=40, width=40,
                corner_radius=10,
                border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=680, y=100)

east = ctk.CTkButton(frame2,
                text="E", font=("Helvetica", 18), text_color="white",
                command=moveEast,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=40, width=40,
                corner_radius=10,
                border_color="white", border_width=2, background_corner_colors=("#27262e", "#27262e", "#27262e", "#27262e"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=780, y=100)

#image saving feature
def saveImage():
    print("Image saved")

save_image = ctk.CTkButton(frame2,
                text="Save Image", font=("Helvetica", 18), text_color="white",
                command=saveImage,
                fg_color="black", bg_color="black", hover_color="dark grey",
                height=30, width=80,
                border_color="white", border_width=2, background_corner_colors=("#653646", "#794c6d", "#b96074", "#b96074"))
save_image.pack(padx=10, pady=10, anchor="nw", expand=1)
save_image.place(x=356, y=680)

frame1.tkraise()
#Run app
root.mainloop()
