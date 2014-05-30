""" Usage Python script to use the RPi to capture LEED images on command      80
# The script interfaces with the RPi GPIO to provide
# two push buttons for control
# And two LED's for information on what is happeneing

# The script will intially light the green LED for 2 second,
# then the red LED for 2 secoonds
# ANd the will switch back to the green LED if it is ready to capture images.

# After a push button command to capture an image while
# the RPi is saving the file the red LED
# Will remain lit and it is ready to caputre again
# when the green LED comes back on

# The second button will immediately terminate the program

# If the LEDs remain on after terminatation then
# the script 'gclean.py' must be run
# This executes the GPIO.cleanup() function to
# free up valuable resources on the RPi

# ******* Note - this script must be run with admin privleges!!!
# If the script is run without admin privleges
# the GPIO will not be accessible

# To run cd to the directory of the script
# and execute 'sudo python picamleed.py'

# Maxwell Grady 2014
"""

import picamera
import RPi.GPIO as GPIO
import time
import sys

#####
# setting up GPIO to get input from a button and control leds
#####


#use BCM pin numbering scheme
GPIO.setmode(GPIO.BCM)

#Create input pin to be used with buttons on pulldown resistor
#Using a pulldown resistor effectively sets
#the button default or OFF position to be LOW

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
buttonpin = 23

# setup two pins for controlling led's to designate when its ok to capture

GPIO.setup(24, GPIO.OUT) #green
grled = 24
#test
GPIO.output(grled, True)
time.sleep(2)
GPIO.output(grled, False)



GPIO.setup(25, GPIO.OUT) #red
rdled = 25
#test
GPIO.output(rdled, True)
time.sleep(2)
GPIO.output(rdled, False)

#setup camera LED control
CAMLED = 5
GPIO.setup(CAMLED, GPIO.OUT)

#setup button to end program
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
endpin = 4


#####
# setting up camera
#####

#create new camera instance -
#this sets up a connection to the CSI port on the RPI main board

camera = picamera.PiCamera()

#hardcode settings to default
#This ensures all settings remain constant upon call to capture function

camera.resolution = (2592, 1944)
camera.brightness = 50 #0-100
camera.contrast = -17 # -100 - 100
camera.saturation = 0 # -100 - 100
camera.sharpness = 0 # -100 - 100
#set to minimal value for minimal gpu post-processing
#camera.exposure_compensation = 0
camera.exposure_mode = 'auto'
camera.awb_mode = 'auto'
camera.shutter_speed = 50000
camera.vflip = True # vflip the picture 180 degrees
camera.ISO = 400 #set ISO



#####
# set up working directories
#####

inc = 52 # increment variable for filenames


#####
# capture image function
#####

def captureLEED(incrmt):
    """This function captures a camera image and gives information via leds
    """
    #turn off green led
    GPIO.output(grled, False)

    #turn on red led
    #GPIO.output(rdled, True)

    #turn off camera led
    GPIO.output(CAMLED, False)

    #call the picamera capture function - output files to highest
    #quality jpeg and potentially
    #embed the raw bayer output in the exif data
    camera.capture(str(incrmt)+".jpg", format='jpeg', quality=100)

    print "Capturing LEED Image"

    #add a manual pause to prevent multiple images from capturing
    time.sleep(1)
    GPIO.output(rdled, True)
    time.sleep(1)
    #turn off red led
    GPIO.output(rdled, False)

    #turn on green led
    GPIO.output(grled, True)

    #turn on camera led
    GPIO.output(CAMLED, True)
    return

#####
# end program call
#####

def endprog(channel):
    """This function cleanly exits the program
    """
    print "ending program"
    GPIO.output(24, False)
    GPIO.output(25, False)
    if camera.closed == True:
        pass
    else:
        camera.close()
    GPIO.output(grled, False)
    GPIO.output(rdled, True)
    time.sleep(0.333)
    GPIO.output(rdled, False)
    time.sleep(0.333)
    GPIO.output(rdled, True)
    time.sleep(0.333)
    GPIO.output(rdled, False)
    time.sleep(0.333)
    GPIO.output(rdled, True)
    time.sleep(0.333)
    GPIO.output(rdled, False)
    GPIO.cleanup()
    sys.exit(0)


#####
# main loop and gpio logic
#####

#loop - when button is pressed and released
#call captureLEED and add one to increment

GPIO.add_event_detect(endpin, GPIO.FALLING, callback=endprog)

while True:
    #try:
    #on button release - call function captureLEED
    #GPIO.FALLING detects the moment the button switches
    #from HIGH to LOW ie. on button release
    GPIO.output(24, True)
    print "waiting for input"
    GPIO.wait_for_edge(buttonpin, GPIO.FALLING)
    captureLEED(inc)
    inc += 2 #stepsize in eV


######
# closing settings
######

#make sure to cleanup to free up the limited RPI resources
#note this code should in principle never execute
#it is only included to ensure clean exit
camera.close()
GPIO.output(24, False)
GPIO.output(25, False)
GPIO.cleanup()
sys.exit(0)
