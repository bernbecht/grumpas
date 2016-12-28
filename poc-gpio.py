import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.IN)
counter = 0

while True:
    if GPIO.input(20):
		counter += 1
		print "! Pin HIGH ",counter
