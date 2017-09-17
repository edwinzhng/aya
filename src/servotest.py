import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(29,GPIO.OUT)

try:
        while True:
            time.sleep(0.015)
            time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
