""" testing again """

import RPi.GPIO as GPIO
import time

global status
status = False
side = 24
front = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(side, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(front, GPIO.IN, pull_up_down= GPIO.PUD_UP)

def GoButton(channel):
    n = 0
    while GPIO.input(channel) == 1:
        n += .1
        time.sleep(.1)
    if .2 < n:
        print('ratatataattta!')
    else:
        pass

def ScrollButton(channel):
    global status
    n = 0
    while GPIO.input(side) == 0:
        n += .1
        time.sleep(.1)
    if .2 <  n <= 2:
        status = 'short'
        n = 0
    elif 2 < n: 
        status = 'long'
        n = 0
    else: 
        status = False
    
GPIO.add_event_detect(front, GPIO.RISING, callback=GoButton, bouncetime=500)
GPIO.add_event_detect(side, GPIO.FALLING, callback=ScrollButton, bouncetime=500)

while True:
    if status:
        print(status)
        status = False
