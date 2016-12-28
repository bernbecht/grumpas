from threading import Thread
from random import randint
import time
import threading
from omxplayer import OMXPlayer
import subprocess
import RPi.GPIO as GPIO
import os.path

BUTTON_GPIO = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.IN)
GPIO.setup(BUTTON_GPIO,GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
	input_state = GPIO.input(BUTTON_GPIO)
	if input_state == False:
			print 'PRESSED'
			time.sleep(0.2)
