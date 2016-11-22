import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)

while True:
    if GPIO.input(21):
        print("! Pin HIGH")
