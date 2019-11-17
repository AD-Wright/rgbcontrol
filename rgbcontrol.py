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

import usb.core
import usb.util
import sys

# Config variables
VENDOR = 0x1017
PRODUCT = 0x900a


# function to open USB connection to mouse
def usbconnect():
    global dev, interface
    dev = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
    interface = 2
    if dev is None:
        raise ValueError("Device not found.  Please plug in mouse.")
    else:
        print("Mouse Found. Connecting...")
    if dev.is_kernel_driver_active(interface):
        print("Kernel interface active, disconnecting it...")
        try:
            dev.detach_kernel_driver(interface)
        except usb.core.USBError as e:
            raise ValueError("Failed to disconnect: %s" % str(e))
    usb.util.claim_interface(dev, interface)
    dev.set_interface_altsetting(interface=interface, alternate_setting=0)

##    for cfg in dev:
##        sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
##        for intf in cfg:
##            sys.stdout.write('\t' + \
##                         str(intf.bInterfaceNumber) + \
##                         ',' + \
##                         str(intf.bAlternateSetting) + \
##                         '\n')
##            for ep in intf:
##                sys.stdout.write('\t\t' + \
##                             str(ep.bEndpointAddress) + \
##                             '\n')

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

def hex2str(h):
	string = "".join("%02x " % b for b in h)
	return string

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

## MAIN PROGRAM ##
# Try to connect to the mouse
usbconnect()

# Set default
setdefault()

# Close connection
usbclose()
