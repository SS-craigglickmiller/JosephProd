""" Testing GPIO """

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
global elapsed

def ButtonPress(channel):
    global start
    global end

    if GPIO.input(23) == 1:
        start = time.time()
        print('Button 1')
        return 0
    if GPIO.input(23) == 0:
        end = time.time()
        elapsed = end - start
        print('Button 2')
        print('Time: ', elapsed)
        return elapsed

def my_print(elapsed):
    print(elapsed)
    if  3 < elapsed <= 5:
        print('3 - 5')
    elif elapsed > 5:
        print('>5')
    else:
        print('press button longer')

#GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback, bouncetime=200)
#GPIO.add_event_callback(23, my_callback)
#GPIO.add_event_callback(23, my_print)

while True:
    marked, ready_for_next = False, False
    while not marked and not ready_for_next:
        try:
            GPIO.wait_for_edge(23, GPIO.BOTH)
            elapsed = ButtonPress(23)
            print(elapsed)
        except KeyboardInterrupt:
            GPIO.cleanup()
    
        if elapsed > 2:
            if marked:
                print('get the next post')
                ready_for_next = True
                elapsed = 0
            else:
                print('ratatatataatt')
                marked = True
                elapsed = 0
        else:
            continue

print('Done')

