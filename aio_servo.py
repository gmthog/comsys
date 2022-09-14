import time
import RPi.GPIO as GPIO

servoPIN = 18 

GPIO.setmode(GPIO.BCM) # Use GPIO Broadcom GPIO numbers (BCM)
GPIO.setup(servoPIN, GPIO.OUT) # Output to send PWM signal to pin 17

p = GPIO.PWM(servoPIN, 50) # PWM on GPIO pin 17 at 50Hz

p.start(0) # Start angle = 0

def open():
    p.ChangeDutyCycle(10) # right +90 deg position
    time.sleep(1)

def close():
    p.ChangeDutyCycle(7.5) # neutral position
    time.sleep(1)

# Setup your channel
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.output(servoPIN, GPIO.LOW)

# To test the value of a pin use the .input method
channel_is_on = GPIO.input(servoPIN)  # Returns 0 if OFF or 1 if ON

if channel_is_on == 1:
    open()
elif channel_is_on == 0:
    close()
    