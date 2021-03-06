# Program to control RGB on J-Tech style vertical mouse
# Author: AD-Wright
# Date: 2019-11-16+
# GPL v3.0
# dependencies: pyusb 1.0 (sudo apt-get install python3-usb)

# To enable non-sudo running of this file, add a file to the /etc/udev/rules.d folder
# with this name: 55-jtech.rules
# and these contents:
# SUBSYSTEM=="usb", ATTRS{idVendor}=="1017", ATTRS{idProduct}=="900a", MODE="666"
# and then execute:
# sudo chmod 644 /etc/udev/rules.d/55-jtech.rules
# sudo chown root. /etc/udev/rules.d/55-jtech.rules
# sudo service udev restart
# Then unplug and replug mouse

import usb.core
import usb.util
import sys
from tkinter import *

# Config variables
VENDOR = 0x1017
PRODUCT = 0x900a
red = 0x00
green = 0x00
blue = 0x00
speed = 0x00
direction = 0x00

# function to open USB connection to mouse
def usbconnect():
    global dev, interface
    dev = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
    interface = 2
    if dev is None:
        raise ValueError("Device not found.  Please plug in / replug mouse.")
    if dev.is_kernel_driver_active(interface):
        try:
            dev.detach_kernel_driver(interface)
        except usb.core.USBError as e:
            raise ValueError("Failed to disconnect: %s" % str(e))
    usb.util.claim_interface(dev, interface)
    dev.set_interface_altsetting(interface=interface, alternate_setting=0)

# function to close the USB connection to the mouse
def usbclose():
    usb.util.release_interface(dev,interface)
    dev.attach_kernel_driver(interface)

# function to send command to the mouse, returns number of bytes sent
def senddata(data):
    ret = dev.ctrl_transfer(
        bmRequestType=0x21,
        bRequest=0x09,
        wValue=0x0300,
        wIndex=0x0002,
        data_or_wLength=data
        )
    
# function to read data from the mouse
def readdata(data):
    senddata(data)
    return dev.ctrl_transfer(
        bmRequestType=0xa1,
        bRequest=0x1,
        wValue=0x0307,
        wIndex=0x0001,
        data_or_wLength=data
        )

# function for printing the hex properly
def hex2str(h):
	string = "".join("%02x " % b for b in h)
	return string

# function to open control channel
def opencontrol():
    senddata([0x03, 0x01, 0x0f, 0xd8, 0x40, 0x00, 0x00, 0xd4])
    senddata([0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfc])
    senddata([0x11, 0x05, 0x08, 0x00, 0x00, 0x00, 0x00, 0xe1])
    
    data1 = [0x01, 0x02, 0x03, 0x04, 0x05, 0x80, 0x80, 0x80, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data1)

    senddata([0x0b, 0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0xea])

# function to close control
def closecontrol():
    senddata([0x12, 0x01, 0x40, 0x00, 0x00, 0x00, 0x00, 0xac])
    
    data5 = [0x01, 0x00, 0xf0, 0x00, 0x01, 0x00, 0xf1, 0x00, \
             0x01, 0x00, 0xf2, 0x00, 0x01, 0x00, 0xf3, 0x00, \
             0x01, 0x00, 0xf4, 0x00, 0x07, 0x00, 0x03, 0x00, \
             0x0a, 0xf0, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data5)
    data6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x04, 0x00, 0x02, 0x00, 0x04, 0x00, 0x01, 0x00]
    dev.write(4,data6)
    
# function to set solid color mode
def solid(r,g,b):
    opencontrol()
    senddata([0x0c, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x72])
    
    data2 = [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data2)
    data3 = [0x0f, 0x04, 0x0a, 0x0a, 0x19, 0x19, 0x05, 0x01, \
             0x05, 0x00, 0x64, 0x64, 0x01, 0xc0, 0xf0, 0x03, \
             0x01, 0x01, 0x64, 0x00, 0x02, 0x03, 0x04, 0x05, \
             0x06, 0x07, 0x07, 0x07, 0x02, 0x03, 0x04, 0x05]
    dev.write(4,data3)

    senddata([0x0d, 0x01, 0x05, 0x00, 0x00, 0x00, 0x00, 0xec])
    senddata([0x10, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0xd6])

    # set color
    if r > 51:
        r = 51
    if g > 51:
        g = 51
    if b > 51:
        b = 51
    # 33 = 51dec = 256 actual. (not full 0-255). Probably power-related.
    color1 = [r, g, b] # "warm-up" color (first couple seconds.  Not implepented as a feature)
    color2 = [r, g, b] # This is actual color Not valid: 7 1a 1f 22 24 26 2b 31
    color3 = [0x33, 0x00, 0x00] #                                       7 26 31 34 36 38 43 49
    color4 = [0x33, 0x00, 0x33] # Total number of available colors: 43 ^ 3 = 79507
    color5 = [0x00, 0x33, 0x33] # Sufficient number: 64
    color6 = [0x33, 0x33, 0x00] # so 4 levels per color: off, 1/3, 2/3, 3/3. 
    color7 = [0x33, 0x33, 0x33] # 0, 0x11, 0x21, 0x33: 0, 17, 33, 51
    end = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data4 = color1 + color2 + color3 + color4 + color5 + color6 + color7 + end
    dev.write(4,data4)
    closecontrol()
    print(hex2str(color1))

# function for "breathing" LEDs
def breathe(r,g,b):
    opencontrol()
    senddata([0x0c, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x72])
    
    data2 = [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data2)
    data3 = [0x0f, 0x04, 0x0a, 0x0a, 0x19, 0x19, 0x05, 0x02, \
             0x0f, 0x00, 0x64, 0x64, 0x01, 0xc0, 0xf0, 0x03, \
             0x01, 0x01, 0x64, 0x00, 0x02, 0x03, 0x04, 0x05, \
             0x06, 0x07, 0x07, 0x07, 0x02, 0x03, 0x04, 0x05]
    dev.write(4,data3)

    senddata([0x0d, 0x02, 0x05, 0x00, 0x00, 0x00, 0x00, 0xeb])
    senddata([0x10, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0xd6])

    # set color
    if r > 51:
        r = 51
    if g > 51:
        g = 51
    if b > 51:
        b = 51
    color1 = [r, g, b] # "warm-up" color (first couple seconds.  Not implemented as a feature)
    color2 = [r, g, b] # This is actual color Not valid: 7 1a 1f 22 24 26 2b 31
    color3 = [r, g, b] #                                 7 26 31 34 36 38 43 49
    color4 = [r, g, b] # Total number of available colors: 43 ^ 3 = 79507
    color5 = [0x00, 0x00, 0x11] # Sufficient number: 64
    color6 = [r, g, b] # so 4 levels per color: off, 1/3, 2/3, 3/3. 
    color7 = [r, g, b] # 0, 0x11, 0x21, 0x33: 0, 17, 33, 51
    end = [r, g, b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data4 = color1 + color2 + color3 + color4 + color5 + color6 + color7 + end
    dev.write(4,data4)
    closecontrol()
    print(hex2str(color1))

# function for "breathing" LEDs
def neon(r,g,b):
    opencontrol()
    senddata([0x0c, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x72])
    
    data2 = [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data2)
    data3 = [0x0f, 0x04, 0x0a, 0x0a, 0x19, 0x19, 0x05, 0x02, \
             0x01, 0x02, 0x64, 0x64, 0x01, 0xc0, 0xf0, 0x03, \
             0x01, 0x01, 0x64, 0x00, 0x02, 0x03, 0x04, 0x05, \
             0x06, 0x07, 0x07, 0x07, 0x02, 0x03, 0x04, 0x05]
    dev.write(4,data3)

    senddata([0x0d, 0x04, 0x05, 0x05, 0x00, 0x00, 0x00, 0xe4])
    senddata([0x10, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0xd6])

    # set color
    if r > 51:
        r = 51
    if g > 51:
        g = 51
    if b > 51:
        b = 51
    color1 = [r, g, b]
    color2 = [r, g, b]
    color3 = [0x33, 0x00, 0x00]
    color4 = [0x33, 0x00, 0x33]
    color5 = [0x00, 0x33, 0x33]
    color6 = [0x33, 0x33, 0x00]
    color7 = [0x33, 0x33, 0x33]
    end = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data4 = color1 + color2 + color3 + color4 + color5 + color6 + color7 + end
    dev.write(4,data4)
    closecontrol()
    print(hex2str(color1))

# function for "breathing" LEDs
def floating(r,g,b,speed,direction):
    opencontrol()
    senddata([0x0c, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x72])
    
    data2 = [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data2)
             #5=f,0c=m,14=s
                   #1 = down, 0 = up
    data3 = [0x0f, 0x04, 0x0a, 0x0a, 0x19, 0x19, 0x05, 0x03, \
             0x05, 0x01, 0x64, 0x64, 0x01, 0xc0, 0xf0, 0x03, \
             0x01, 0x01, 0x64, 0x00, 0x02, 0x03, 0x04, 0x05, \
             0x06, 0x07, 0x07, 0x07, 0x02, 0x03, 0x04, 0x05]
    dev.write(4,data3)
                          #5=f,0c=m,14=s
                                #1 = down, 0 = up
    senddata([0x0d, 0x03, 0x05, 0x01, 0x00, 0x00, 0x00, 0xe4])
    senddata([0x10, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0xd6])

    # set color
    if r > 51:
        r = 51
    if g > 51:
        g = 51
    if b > 51:
        b = 51
    color1 = [r, g, b]
    color2 = [0x00, 0x00, 0x33]
    color3 = [0x33, 0x00, 0x00]
    color4 = [0x33, 0x00, 0x33]
    color5 = [0x00, 0x33, 0x33]
    color6 = [0x33, 0x33, 0x00]
    color7 = [0x33, 0x33, 0x33]
    end = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data4 = color1 + color2 + color3 + color4 + color5 + color6 + color7 + end
    dev.write(4,data4)
    closecontrol()
    print(hex2str(color1))
    
# function to set factory default
def setdefault():
    print("### SETTING FACTORY DEFAULT ###")
    print("Opening control channel...")
    senddata([0x03, 0x01, 0x0f, 0xd8, 0x40, 0x00, 0x00, 0xd4])
    senddata([0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfc])
    senddata([0x11, 0x05, 0x08, 0x00, 0x00, 0x00, 0x00, 0xe1])
    
    data1 = [0x01, 0x02, 0x03, 0x04, 0x05, 0x80, 0x80, 0x80, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data1)

    senddata([0x0b, 0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0xea])
    senddata([0x0c, 0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x71])
    
    data2 = [0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data2)

    data3 = [0x0f, 0x04, 0x0a, 0x0a, 0x19, 0x19, 0x05, 0x03, \
             0x05, 0x00, 0x64, 0x64, 0x01, 0xc0, 0xf0, 0x03, \
             0x01, 0x01, 0x64, 0x00, 0x02, 0x03, 0x04, 0x05, \
             0x06, 0x07, 0x07, 0x07, 0x02, 0x03, 0x04, 0x05]
    dev.write(4,data3)

    senddata([0x0d, 0x03, 0x05, 0x00, 0x00, 0x00, 0x00, 0xea])
    senddata([0x10, 0x01, 0x18, 0x00, 0x00, 0x00, 0x00, 0xd6])

    print("Sending colors...")
    color1 = [0x00, 0x33, 0x00]
    color2 = [0x00, 0x00, 0x33]
    color3 = [0x33, 0x00, 0x00]
    color4 = [0x33, 0x00, 0x33]
    color5 = [0x00, 0x33, 0x33]
    color6 = [0x33, 0x33, 0x00]
    color7 = [0x33, 0x33, 0x33]
    end = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data4 = color1 + color2 + color3 + color4 + color5 + color6 + color7 + end
    dev.write(4,data4)
    
    print("Closing channel...")
    senddata([0x12, 0x01, 0x40, 0x00, 0x00, 0x00, 0x00, 0xac])
    
    data5 = [0x01, 0x00, 0xf0, 0x00, 0x01, 0x00, 0xf1, 0x00, \
             0x01, 0x00, 0xf2, 0x00, 0x01, 0x00, 0xf3, 0x00, \
             0x01, 0x00, 0xf4, 0x00, 0x07, 0x00, 0x03, 0x00, \
             0x0a, 0xf0, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00]
    dev.write(4,data5)
    data6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, \
             0x04, 0x00, 0x02, 0x00, 0x04, 0x00, 0x01, 0x00]
    dev.write(4,data6)
    print("###     RESET COMPLETE      ###")

# function for rgb grid
def rgb_grid(i,j):
    # 4-bit rgb: 0, 17, 33, 51 are the available options
    colors = [0x00, 0x11, 0x21, 0x32]
    if i < 4 and j < 4:
        red = colors[0]
    elif i > 4 and j < 4:
        red = colors[1]
    elif i < 4 and j > 4:
        red = colors[2]
    else:
        red = colors[3]
    green = colors[i%4]
    blue = colors[j%4]
    return (red, green, blue)



## MAIN PROGRAM ##
root = Tk()
previewcolor = StringVar()
mode = StringVar()

def click(event):
    global red, green, blue
    xc = int(event.x / 40)
    yc = int(event.y / 40)
    if xc < 8:
        (red, green, blue) = rgb_grid(xc,yc)
        selection.configure(bg = "#%02x%02x%02x" % (red*5, green*5, blue*5))
        if mode.get() == "0":
            solid(0, 0, 0)
        elif mode.get() == "1":
            solid(red, green, blue)
        elif mode.get() == "2":
            breathe(red, green, blue)
        elif mode.get() == "3":
            floating(red, green, blue)
        elif mode.get() == "4":
            neon(red, green, blue)
        root.update()

def lightoff():  # radio button of "Off" selected
    global red, green, blue
    if mode.get() == "0":
        solid(0, 0, 0)
    elif mode.get() == "1":
        solid(red, green, blue)
    elif mode.get() == "2":
        breathe(red, green, blue)
    elif mode.get() == "3":
        floating(red, green, blue)
    elif mode.get() == "4":
        neon(red, green, blue)
    root.update()

# make the gui
canvas = Canvas(root, width=320, height=320)
canvas.bind("<Button-1>", click) # bind mouse click

# create grid of "4-bit" colors
for i in range(0, 8):
    for j in range(0, 8):
        x0 = i * 40 + 2
        y0 = j * 40 + 2
        (red, green, blue) =  rgb_grid(i,j)
        color = "#%02x%02x%02x" % (red*5, green*5, blue*5)
        previewcolor.set(color)
        canvas.create_rectangle(x0, y0, x0 + 36, y0 + 36, fill = color, width = 0)
canvas.grid(row = 0, column = 0, rowspan = 11)

# create "preview" pane
selection = Label(root, bg=previewcolor.get(), padx = 50, pady = 50)
selection.grid(row = 0, column = 1)

# create mode selection radio buttons
MODES = [("Off", "0"),("Solid","1"),("Breathe", "2"),("Floating", "3"),("Neon","4")]
mode.set("1")
for text, temp in MODES:
    button = Radiobutton(root, text=text, variable=mode, value=temp, indicatoron=0, command=lightoff)
    button.grid(row = int(temp) + 2, column = 1, sticky = W+E+N+S)
    

# create exit button
Button(root, text="Save & Exit", command=root.destroy).grid(row = 10, column = 1)

# Try to connect to the mouse
usbconnect()

# main program loop
root.mainloop()

# Close connection
usbclose()
