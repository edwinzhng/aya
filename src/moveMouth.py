import RPi.GPIO as GPIO
import threading
import time

p = None
shouldStop = False

def initialize():
    global p
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    p = GPIO.PWM(12, 50)
    p.start(7.5)

def stopActuate():
    global shouldStop
    shouldStop = True

def moveMouth(time):
    global shouldStop
    shouldStop = False
    time.sleep(0.5)
    threading.Thread(target = actuate).start()
    threading.Timer(time, stopActuate).start()

def actuate():
    global shouldStop
    global p
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
