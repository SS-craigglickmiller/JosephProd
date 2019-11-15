""" testing again """

import RPi.GPIO as GPIO
import time

go = 23
scroll = 24
count_go = 0
count_scroll = 0
global go_status
global scroll_status
go_status = False
scroll_status = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(go, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(scroll, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('Status Big: ', GPIO.input(go))
print('Status Little: ', GPIO.input(scroll))

def ButtonPress(channel):
    global button_status
    global start
    button_status = False
    if GPIO.input(channel) == 1:
        start = time.time()
        print('Status1: ', GPIO.input(go))
    if GPIO.input(channel) == 0:
        button_time = time.time() - start
        print('Status2: ', GPIO.input(go))
        print(button_time)
        if button_time < 1:
            button_status = False
        if 1 <= button_time:
            button_status = True

def ButtonPress1(channel):
    global go_status
    time.sleep(0.5)
    if GPIO.input(go) == 1:
        print('Status Big: ', GPIO.input(go))
        go_status = True
    else:
        print('Status Big: Press longer')
        go_status = False

def ScrollButton(channel):
    global scroll_status
    i = 0.5
    time.sleep(0.5)
    if GPIO.input(scroll) == 0:
        while GPIO.input(scroll) != 1:
            i += .1
            time.sleep(.1)
        if i >= 5:
            print('Status Little: ', GPIO.input(scroll))
            scroll_status = 'previous'
        else:
            scoll_status = 'next'
    else:
        scroll_status = False

GPIO.add_event_detect(go, GPIO.FALLING, callback=ButtonPress1, bouncetime=200)
GPIO.add_event_detect(scroll, GPIO.FALLING, callback=ScrollButton, bouncetime=200)
while True:
    #try:
    #    GPIO.wait_for_edge(go, GPIO.BOTH)
    #except KeyboardInterrupt:
    #    GPIO.cleanup()
    #ButtonPress(go)
    if go_status:
        print('send it!')
        count_go += 1
        print('Go: ', count_go)
        go_status = False
    elif scroll_status == 'next':
        print('scroll to next')
        count_scroll += 1
        print('Scroll: ', count_scroll)
        scroll_status = False
    elif scroll_status == 'previous':
        print('show previous')
        scroll_status = False
    else:
        time.sleep(.2)
        continue
GPIO.cleanup()

