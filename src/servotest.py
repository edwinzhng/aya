import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50)

p.start(7.5)

def startServo():
    while True:
	p.ChangeDutyCycle(30)  # turn towards 90 degree
	time.sleep(0.2) # sleep 1 second
	p.ChangeDutyCycle(2.5)  # turn towards 0 degree
	time.sleep(0.2) # sleep 1 second
	p.ChangeDutyCycle(18) # turn towards 180 degree
    time.sleep(0.2) # sleep 1 second

def stopServo():
	p.stop()
        GPIO.cleanup()
