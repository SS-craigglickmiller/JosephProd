""" testing again """

import RPi.GPIO as GPIO
import time

global elapsed
global status
elapsed = 0
status = False
front = 23
side = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(front, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(side, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def ButtonPress(channel):
    global elapsed
    global status

    start = time.time()
    what = GPIO.wait_for_edge(channel, GPIO.BOTH, timeout=10000)
    print('edge returns: ', what)
    elapsed = time.time() - start
    if elapsed >= 10:
        pass
    elif channel == 23:
        status = 'front'
    elif channel == 24:
        if elapsed > 2:
            status = 'previous'
        else:
            status = 'next'
    else:
        pass
    

GPIO.add_event_detect(front, GPIO.RISING, callback=ButtonPress, bouncetime=500)
GPIO.add_event_detect(side, GPIO.FALLING, callback=ButtonPress, bouncetime=500)

while True:
    if status:
        print(status)
        status = False
