import RPi.GPIO as GPIO
import smbus
import sys
import time
import atexit

ZONE_GPIO = {1: 15, 2: 13}

GPIO.setmode(GPIO.BOARD)
bus = smbus.SMBus(1)

#I2C addres
address = 0x4d


GPIO.setup(15, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

quit = False

def waterLawn(zone,durr):
    global quit
    durr = int(durr)
    durr = durr * 60
    GPIO.output(ZONE_GPIO[int(zone)], GPIO.HIGH)
    print("starting zone %s GPIO %s" % (zone, ZONE_GPIO[int(zone)]))
    while not quit and durr > 0:
        time.sleep(1)
        durr = durr - 1
    GPIO.output(ZONE_GPIO[int(zone)], GPIO.LOW)
    print("stopping zone %s" % zone)

def stahp():
    global quit
    quit = True
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    print("exit caught, stopping all zones")

def main():
    waterLawn(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    atexit.register(stahp)
    main()
