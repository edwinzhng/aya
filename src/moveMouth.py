import RPi.GPIO as GPIO
import time

def actuate():
        while True:
		p.ChangeDutyCycle(25)
		time.sleep(0.15)
		p.ChangeDutyCycle(2.5)
		time.sleep(0.15)
		p.ChangeDutyCycle(18)
        time.sleep(0.15)
