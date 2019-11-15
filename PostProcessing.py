""" Interface for the Joseph Machine. Import CSV of finished posts and process.

"""

import I2C_LCD_driver
import csv
import math
import logging
import datetime
import serial
import subprocess

# Connect to USB-serial cable
ser = serial.Serial('/dev/ttyUSB0')
# Settings for connection
ser.baudrate = 9600
ser.parity = serial.PARITY_NONE
ser.stopbit = serial.STOPBITS_ONE
ser.bytesize = serial.EIGHTBITS
ser.xonxoff = False
ser.rtscts = False

# get IP address
myip = subprocess.check_output(['hostname', '-I'])

# Initialize the LCD Interface
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()
mylcd.lcd_display_string('200120    |  7 (20)',1)
mylcd.lcd_display_string('Black     |  36 BR-D',2)
mylcd.lcd_display_string('Autoweld  |  Std',3)


