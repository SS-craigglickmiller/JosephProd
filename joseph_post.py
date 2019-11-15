""" This script handles data after the Joseph fabricates a post. 

Inputs:
    - 'Label' files from Stuff share (192.168.1.250\craig\craig\Joseph\Production\Labels)
    - Each file has meta data about a post, written when post fabrication completes.

Outputs:
    - parse file for traceability about the post
    - update the LCD screen
    - Set the pattern for the dot peener and load post info
    - light up the appropriate pick light for the foot
    - when the go button is pushed, fire the peener and move to the next file

"""

import serial
import os
import subprocess
import RPi.GPIO as GPIO
import datetime
import time
import logging
import csv
import I2C_LCD_driver
import manage_files

#######################################################################
##### LOGGING #####
#######################################################################

manage_files.DeleteFiles('/home/pi/Joseph/Scripts/Log/', 365)
filename = '/home/pi/Joseph/Scripts/Log/' + str(datetime.date.today()) + '-Joseph-processing.log'
logger = logging.getLogger('__name__')
hdlr = logging.FileHandler(filename)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.info('--------------------------------------')
logger.info('Post Production of aluminum posts on Joseph')

#######################################################################
#####  Connect to USB-serial cable
#######################################################################
logger.info('Connect to dot peener...')
ser = serial.Serial('/dev/ttyUSB0')
# Settings for connection
ser.baudrate = 9600
ser.parity = serial.PARITY_NONE
ser.stopbit = serial.STOPBITS_ONE
ser.bytesize = serial.EIGHTBITS
ser.xonxoff = False
ser.rtscts = False

#######################################################################
#####   GPIO for button press
#######################################################################

GO = 23 # Green go button pin#
SIDE = 24 # side button pin#
global status
status = False
GPIO.setmode(GPIO.BCM)
GPIO.setup(SIDE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GoButtonPress(channel):
    global status
    n = 0
    while GPIO.input(channel) == 1:
        n += .1
        time.sleep(.1)
    if .2 < n:
        status = 'Go Button'
    else:
        pass

def SideButtonPress(channel):
    global status
    n = 0
    while GPIO.input(channel) == 0:
        n += .1
        time.sleep(.1)
    if .2 < n <= 2:
        status = 'Side Short'
    elif 2 < n:
        status = 'Side Long'
    else: 
        pass

GPIO.add_event_detect(GO, GPIO.RISING, callback=GoButtonPress, bouncetime=500)
GPIO.add_event_detect(SIDE, GPIO.FALLING, callback=SideButtonPress, bouncetime=500)

#######################################################################
##### Initialize the LCD Interface
#######################################################################

myip = subprocess.check_output(['hostname', '-I'])
logger.info('Initialize the LCD display.')
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()
mylcd.lcd_display_string('StairSupplies',1)
mylcd.lcd_display_string('Joseph Machine',2)
mylcd.lcd_display_string('PRESS SIDE BUTTON',3)
mylcd.lcd_display_string('IP: ' + str(myip)[2:17], 4)


#######################################################################
##### CONSTANTS #####
#######################################################################
PATH = '/mnt/stuff/Joseph/Production/Labels'

# Initialize variables
wip = {}
current = False
posts = {}
previous = False

#######################################################################
##### Post Class #####
#######################################################################

class PostDetails():
    
    routing_inst = {
            'Joseph:Autoweld':'Weld',
            'Joseph:Additional Milling':'Additional Milling',
            'Joseph:Angle Cutoff':'Angle cutoff at ',
            'Joseph:Manual weld':'Manual weld',
            'Joseph:See Print':'See Print!',
        }
    pc_color = {
            'PC: Black':'BK',
            'PC Fluoropolymer: Antique Bronze':'F-AB',
            'PC Fluoropolymer: Apollo White':'F-AP',
            'PC Fluoropolymer: Black':'F-BK',
            'PC Fluoropolymer: Bone White':'F-BW',
            'PC Fluoropolymer: Colonial Grey':'F-CG',
            'PC Fluoropolymer: Fashion Grey':'F-FG',
            'PC Fluoropolymer: Platinum Matte':'F-PM',
            'PC Fluoropolymer: Silver Spark':'F-SP',
            'PC Fluoropolymer: Speedboat Silver':'F-SP',
            'PC: Apollo White':'AP',
            'PC: Bone White':'BW',
            'PC: Bronze Akzonobel GM2007':'BZ',
            'PC: Brushed Aluminum w/ Clear - SRSF-90299':'B-Cl',
            'PC: Brushed w/ Clear':'B-CL',
            'PC: Charcoal':'CH',
            'PC: Clear Finish':'Cl',
            'PC: Colonial Grey':'CG',
            'PC: Copper Vein':'CV',
            'PC: Fashion Grey':'FG',
            'PC: Hunter Green':'HG',
            'PC: Light Blue':'LBl',
            'PC: Lithonia Bronze':'LBz',
            'PC: Mineral Bronze':'MBz',
            'PC: Rust Spice':'RS',
            'PC: Sandstone':'SD',
            'PC: Seawolf':'SW',
            'PC: Speedboat Silver':'SB',
            'PC: Super C-33 Bronze':'Bz',
            'PC: Tube Brown':'TB',
        }

    foot = {
            'Angle':['Angle', 'SHIFTED'],
            'Core Drill':['No Foot','None'],
            'Narrow Angle':['Narrow','SHIFTED'],
            'Ramp':['Standard','SHIFTED'],
            'Side Mount Inside Corner Plate':['ISC','STRAIGHT'],
            'Side Mount Outside Corner Plate':['OSC','STRAIGHT'],
            'Side Mount Plate':['Side','STRAIGHT'],
            'Slim Side Mount Bump Out':['No Foot','None'],
            'Special Application Foot':['Special','SHIFTED'],
            'Standard Foot':['Standard','SHIFTED'],
            '':'Update!',
        }

    top = {
            'Universal Top':'UnivTop',
            'Flat Top':'FlatTop',
        }

    def __init__(self, post):
        self.post = post
        self.order_number = post[0]
        self.metal_production_date = post[1]
        self.due_date = post[2]
        self.post_number = post[3]
        self.configuration = post[4]
        self.mounting = post[5]
        self.top_style = self.top.get(post[6], 'Unknown')
        self.foot_style = self.foot[post[7]]
        self.angle = post[8]
        self.cut_length = post[9]
        self.routing = self.routing_inst.get(post[10],'See print!')
        self.color = self.pc_color[post[11]]
        self.infill = post[12]
        self.serial_number = post[13]
        self.item_count = post[14]
        self.part_number = post[15]
        self.order_and_num = self.order_number + ' #' + self.post_number

    def UpdateDisplay(self):
        """ This method updates the LCD screen, Dot Peener program, and pick lights."""

        # Update the LCD
        mylcd.lcd_clear()
        start = int((19 - len(self.order_and_num))/2)
        mylcd.lcd_display_string(self.order_and_num, 1, start)
        mylcd.lcd_display_string(self.top_style, 2)
        if self.infill == 'Slim Rod':
            R2 = 'Rod ' + self.configuration
        else: 
            R2 = self.infill + ' ' + self.configuration
        right = len(R2)
        mylcd.lcd_display_string(R2, 2, 20-right)
        mylcd.lcd_display_string(self.foot_style[0], 3)
        if self.angle:
            right = len(self.angle)+4
            mylcd.lcd_display_string('Ang:' + self.angle, 3, 20-right)
        else:
            mylcd.lcd_display_string('Ang:-', 3, 20-5)
        if self.foot_style[0] in ['Angle', 'Narrow']:
            mylcd.lcd_display_string(self.routing + str(90 - float(self.angle)), 4)
        else:
            mylcd.lcd_display_string(self.routing, 4)

        # Update the peener
        if self.foot_style[1]:
            send_pattern = '{}P{}' + self.foot_style[1] + '{}{}'
            send_pattern = send_pattern.format(chr(1), chr(2), chr(3), chr(13))
            response = ser.write(send_pattern.encode())
            send_ordernum = '{}1{}01' + self.order_and_num + '{}{}'
            send_ordernum = send_ordernum.format(chr(1),chr(2),chr(3),chr(13))
            response += ser.write(send_ordernum.encode())
            send_color = '{}1{}03' + self.color + '{}{}'
            send_color = send_color.format(chr(1),chr(2),chr(3),chr(13))
            response += ser.write(send_color.encode())
        else:
            send_pattern = '{}P{}SHIFTED{}{}'
            send_pattern = send_pattern.format(chr(1),chr(2),chr(3),chr(13))
            response = ser.write(send_pattern.encode())

        #TODO add pick light here 
        return 'Done'

    def MarkFoot(self):
        sendit = '{}G{}{}{}'
        sendit = sendit.format(chr(1), chr(2), chr(3), chr(13))
        ser.write(sendit.encode())

#######################################################################
##### HELPER FUNCTIONS #####
#######################################################################

def GetCSVData(filename):
    """ Read in the label file exported after a post is produced. 
    Line 13 has the post details in it. """
    this_label = []
    try:
        f = open(filename, newline='')
    except:
        message = 'Could not open ' + filename
        print(message)
        logger.error(message)
    with f:
        this_file = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in this_file:
            this_label.append(row)
    this_post = this_label[13]
    this_post = [i.replace("'","") for i in this_post]
    this_post[0] = this_post[0].split('[')[1] # clean up the first item
    this_post[-1] = this_post[-1][:-1] # Trim the final ] on the last list item
    this_post = [i.strip() for i in this_post] # strip leading/trailing white space
    return this_post

def GetFiles(posts):
    for filename in os.listdir(PATH):
        if os.path.isfile(os.path.join(PATH,filename)):
            timestamp = filename.split('_')[-1].split('.')[0]
            posts[timestamp] = GetCSVData(os.path.join(PATH, filename))
            manage_files.ArchiveSingle(PATH, filename)
    return posts


#######################################################################
##### Main Loop
#######################################################################

while True: 
    if status == 'Go Button':
        if previous:
            PreviousPost.MarkFoot()
        if current:
            CurrentPost.MarkFoot()
        status = False
    elif status == 'Side Short':
        if previous:
            CurrentPost.UpdateDisplay()
            previous = False
            status = False
        else:
            if current:
                PreviousPost = PostDetails(current)
            wip = GetFiles(wip)
            if len(wip): 
                current = wip.pop(sorted(wip)[0])
                CurrentPost = PostDetails(current)
            else:
                mylcd.lcd_clear()
                mylcd.lcd_display_string('No posts in WIP', 1)
                mylcd.lcd_display_string('PRESS SIDE BUTTON', 3)
            status = False
    elif status == 'Side Long':
        PreviousPost.UpdateDisplay()
        previous = True
        status = False
    else:
       pass

GPIO.cleanup()


