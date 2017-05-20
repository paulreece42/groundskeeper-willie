#!/bin/env python3

import threading
import atexit
from flask import Flask
from flask_ask import Ask, statement
import time
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import logging
import RPi.GPIO as GPIO
import smbus

MAX_DURATION_MINUTES = 60
DEFAULT_DURATION = 5
VALID_ZONES = [1,2]
ZONE_NAMES = { 1: "front yard", 2: "back yard" }
ZONE_GPIO = {1: 15, 2: 13}

GPIO.setmode(GPIO.BOARD)
bus = smbus.SMBus(1)

#I2C addres
address = 0x4d


GPIO.setup(15, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)


logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
ask = Ask(app, '/')

executor = ThreadPoolExecutor(max_workers=1)
quit = False

def waterLawn(zone,durr):
    global quit
    durr = durr * 60
    GPIO.output(ZONE_GPIO[int(zone)], GPIO.HIGH)
    print("starting zone %s GPIO %s" % (zone, ZONE_GPIO[int(zone)]))
    while not quit and durr > 0:
        time.sleep(1)
        durr = durr - 1
    GPIO.output(ZONE_GPIO[int(zone)], GPIO.LOW)
    print("stopping zone %s" % zone)


@ask.intent('WaterZone')
def hello(zone):
    global quit
    if int(zone) in VALID_ZONES and (GPIO.input(15) + GPIO.input(13)) == 0:
        logging.info("Watering zone %s for %s" % (zone, DEFAULT_DURATION))
        quit = False
        executor.submit(waterLawn,zone,DEFAULT_DURATION)
        speech_text = "Aye, I'll water yer stupid %s" % ZONE_NAMES[int(zone)]
        return statement(speech_text).simple_card('Watering zone %s for %s minutes' % (zone,DEFAULT_DURATION))
    elif (GPIO.input(15) + GPIO.input(13)) > 0:
        logging.info("already watering")
        speech_text = "Willie can only do so much! Willie is already watering!"
        return statement(speech_text).simple_card('Stop watering the other zone first')
    elif int(zone) not in VALID_ZONES:
        stringZones = ' '.join(str(e) for e in VALID_ZONES)
        logging.warning("Zone %s is not in valid zones: %s" % (zone, stringZones))
        speech_text = "Shut ye geggie, all Willie can do are zones %s" % stringZones
        return statement(speech_text).simple_card("""What Willie is trying to say is: "You're an idiot, try one of these zones next time: %s" """ % stringZones)
    else:
        speech_text = """Awa' n bile your head, trying to confuse Willie!"""
        return statement(speech_text).simple_card("""What Willie is trying to say is: "the jerk who programmed this was too lazy to add a proper response for whatever error condition you've triggered." """)

@ask.intent('WaterZoneDurr')
        speech_text = ""Not yet implemented"""
        return statement(speech_text).simple_card("""What Willie is trying to say is: "the jerk who programmed this was too lazy to add a proper response for whatever error condition you've triggered." """)

@ask.intent('AMAZON.StopIntent')
def stahp():
    global quit
    quit = True
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
    speech_text = """Aye, Willie's going to have a beer"""
    return statement(speech_text).simple_card("""All zones stopped""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
