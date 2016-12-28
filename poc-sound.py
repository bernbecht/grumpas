import os
import time
import subprocess
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.IN)
counter = 0

player = subprocess.Popen(['omxplayer','/home/pi/Music/m.mp3'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds = True)


while counter < 5:
    if GPIO.input(20):
		print "! Pin HIGH ",counter
		player.stdin.write('-')
		time.sleep(0.1)
		counter += 1

player.stdin.write('q')


