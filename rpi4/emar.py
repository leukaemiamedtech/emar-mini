#!/usr/bin/env python3
""" EMAR MINI

EMAR Mini is an open-source Emergency Assistance Robot protptype.
The project is a proof of concept designed to assist doctors, nurses
and hospital staff during the situations similar to  the COVID-19
pandemic that we may face in the future.

MIT License

Copyright (c) 2021 Asociación de Investigacion en Inteligencia Artificial
Para la Leucemia Peter Moss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contributors:
- Adam Milton-Barker

"""

import json
import psutil
import requests
import signal
import sys
import threading
import time

import RPi.GPIO as GPIO

from flask import Flask, Response, request
from threading import Thread

from modules.helpers import helpers
from modules.mqtt import mqtt
from modules.realsenseRead import realsenseRead
from modules.realsenseStream import realsenseStream
from modules.socket import socket

class emar():
    """ EMAR MINI

    EMAR Mini is an open-source Emergency Assistance Robot protptype.
    The project is a proof of concept designed to assist doctors, nurses
    and hospital staff during the situations similar to  the COVID-19
    pandemic that we may face in the future.
    """

    def __init__(self):
        """ Initializes the class. """

        self.helpers = helpers("EMAR")
        self.confs = self.helpers.confs
        self.credentials = self.helpers.credentials

        # Starts the socket module
        self.socket = socket()
        self.ip = self.helpers.get_ip_addr()
        self.port = self.credentials["server"]["port"]

        self.helpers.logger.info("EMAR Mini awaiting commands.")
        self.helpers.logger.info("EMAR Mini Emergency Assistance Robot Class initialization complete.")

    def iotConnection(self):
        """ Initiates the iotJumpWay connection. """

        self.mqtt = mqtt(self.helpers, "EMAR Mini", {
            "host": self.credentials["iotJumpWay"]["host"],
            "port": self.credentials["iotJumpWay"]["port"],
            "location": self.credentials["iotJumpWay"]["location"],
            "entity": self.credentials["iotJumpWay"]["entity"],
            "name": self.credentials["iotJumpWay"]["name"],
            "un": self.credentials["iotJumpWay"]["un"],
            "up": self.credentials["iotJumpWay"]["up"]
        })
        self.mqtt.configure()
        self.mqtt.start()
        self.mqtt.subscribe()
        self.mqtt.commandsCallback = self.commands

    def hardware(self):
        """ Loads the EMAR Mini hardware modules. """

        # Head Servo 1
        h1Pin = 18
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(h1Pin, GPIO.OUT)
        self.h1 = GPIO.PWM(h1Pin, 50)
        self.h1.start(7)
        time.sleep(0.5)
        self.h1.ChangeDutyCycle(0)

        # Arm Servo 1
        a1Pin = 12
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(a1Pin, GPIO.OUT)
        GPIO.setwarnings(False)
        self.a1 = GPIO.PWM(a1Pin, 50)
        self.a1.start(7)
        time.sleep(0.5)
        self.a1.ChangeDutyCycle(0)

        # Arm Servo 2
        a2Pin = 13
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(a2Pin, GPIO.OUT)
        GPIO.setwarnings(False)
        self.a2 = GPIO.PWM(a2Pin, 50)
        self.a2.start(7)
        time.sleep(0.5)
        self.a2.ChangeDutyCycle(0)

        self.helpers.logger.info("EMAR Mini hardware modules loaded.")

    def commands(self, topic, payload):
        """
        iotJumpWay Commands Callback

        The callback function that is triggered in the event of a
        command communication from the iotJumpWay.
        """

        self.helpers.logger.info("Recieved iotJumpWay Command Data : " + payload.decode())
        command = json.loads(payload.decode("utf-8"))
        cycle = 0
        servo = None

        if(command["Type"]=="Head"):
            if(command["Value"]=="RIGHT"):
                cycle = 2.0
                servo = self.h1
            if(command["Value"]=="LEFT"):
                cycle = 12.0
                servo = self.h1
            if(command["Value"]=="CENTER"):
                cycle = 7.0
                servo = self.h1
        if(command["Type"]=="Arm"):
            if(command["Value"]=="2UP"):
                cycle = 7.0
                servo = self.a1
            if(command["Value"]=="2DOWN"):
                cycle = 12.0
                servo = self.a1
            if(command["Value"] == "UP"):
                cycle = 7.0
                servo = self.a2
            if(command["Value"]=="DOWN"):
                cycle = 12.0
                servo = self.a2

        servo.ChangeDutyCycle(cycle)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def life(self):
        """ Sends vital statistics to HIAS """

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()[2]
        hdd = psutil.disk_usage('/').percent
        print(psutil.sensors_temperatures()['cpu_thermal'][0].current)
        tmp = psutil.sensors_temperatures()['cpu_thermal'][0].current
        r = requests.get('http://ipinfo.io/json?token=' +
                self.credentials["iotJumpWay"]["ipinfo"])
        data = r.json()
        if "loc" in data:
            location = data["loc"].split(',')
        else:
            location = [0,0]

        # Send iotJumpWay notification
        self.mqtt.publish("Life", {
            "CPU": str(cpu),
            "Memory": str(mem),
            "Diskspace": str(hdd),
            "Temperature": str(tmp),
            "Latitude": float(location[0]),
            "Longitude": float(location[1])
        })

        self.helpers.logger.info("HIASCDI life statistics published.")
        threading.Timer(300.0, self.life).start()

    def threading(self):
        """ Starts the EMAR Mini software threads. """

        # Life thread
        Thread(target=self.life, args=(), daemon=True).start()

        # Realsense threads
        Thread(target=realsenseRead.run, args=(self, ), daemon=True).start()
        Thread(target=realsenseStream.run, args=(self, ), daemon=True).start()

    def signal_handler(self, signal, frame):
        self.helpers.logger.info("Disconnecting")
        sys.exit(1)


emar = emar()
app = Flask(__name__)

def main():
    signal.signal(signal.SIGINT, emar.signal_handler)
    signal.signal(signal.SIGTERM, emar.signal_handler)

    emar.iotConnection()
    emar.hardware()
    emar.threading()

    app.run(host=emar.ip, port=emar.port)

if __name__ == "__main__":
    main()
