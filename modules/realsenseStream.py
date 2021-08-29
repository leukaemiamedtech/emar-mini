#!/usr/bin/env python3
""" EMAR MINI Realsense D415 Streamer Module

The Realsense D415 Reader module streams frames from the
RealSense D415 camera.

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

import base64
import cv2
import sys
import time

import numpy as np

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread

from io import BytesIO
from PIL import Image

from modules.helpers import helpers

capture = None

class realsenseStream(Thread):
    """ Realsense D415 Streamer Module

    The Realsense D415 Reader module streams frames from the
    RealSense D415 camera.
    """

    def __init__(self):
        """ Initializes the class. """

        self.helpers = helpers("Realsense D415 Streamer")
        super(realsenseStream, self).__init__()
        self.helpers.logger.info(
            "Realsense D415 Streamer Module initialization complete.")

    def run(self):
        """ Runs the module. """
        global capture

        self.ip = self.helpers.get_ip_addr()
        self.socketPort = self.helpers.credentials["socket"]["port"]
        self.serverPort = self.helpers.credentials["stream"]["port"]

        # Allows time for socket server to start
        self.helpers.logger.info(
            "Realsense D415 Streamer waiting 2 seconds for CamRead socket server.")
        time.sleep(2)
        self.helpers.logger.info(
            "Realsense D415 Streamer continuing.")
        # Subscribes to the socket server
        capture = self.socket.subscribe()

        try:
            # Starts web server
            server = ThreadedHTTPServer((self.ip, int(self.serverPort)), CamHandler)
            self.helpers.logger.info(
                "Realsense D415 Streamer server started on http://" \
                    + self.ip + ":" + str(self.serverPort))
            server.serve_forever()
        except KeyboardInterrupt:
            # Closes socket server
            capture.close()
            exit()

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Responds to .mjpg requests
        if self.path.endswith('.mjpg'):
            # Sets headers and response
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            try:
                while True:
                    # Gets processed frame from socket server
                    frame = capture.recv_string()
                    # Decodes the frame
                    frame = cv2.imdecode(np.fromstring(
                        base64.b64decode(frame),
                        dtype=np.uint8), 1)
                    # Converts image to RGB
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Converts rgb array to jpg image
                    jpg = Image.fromarray(rgb)
                    # Creates a temporary file
                    tmpFile = BytesIO()
                    # Saves the jpg to the temp file
                    jpg.save(tmpFile,'JPEG')
                    # Set boundaries
                    self.wfile.write("--jpgboundary".encode())
                    # Finish headers
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(tmpFile.getbuffer().nbytes))
                    self.end_headers()
                    # Send the frame to the browser
                    self.wfile.write(tmpFile.getvalue())
            except Exception as e:
                print("errror " + str(e))
                return
            return

        else:
            # Sets headers and response
            self.send_response(403)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""