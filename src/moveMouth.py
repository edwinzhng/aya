import RPi.GPIO as GPIO
import threading
import time

p = None
shouldStop = False

def initialize():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    p = GPIO.PWM(12, 50)
    p.start(7.5)

def stopActuate():
    global shouldStop
    shouldStop = True

def moveMouth(time):
    threading.Thread(target = Actuator).start()
    threading.Timer(time, stopActuate)

def actuate():
    global shouldStop
    while not shouldStop:
        p.ChangeDutyCycle(25)
        time.sleep(0.15)
        p.ChangeDutyCycle(2.5)
        time.sleep(0.15)
        p.ChangeDutyCycle(18)
        time.sleep(0.15)

class Actuator(threading.Thread):
    def run(self):
        actuate()
