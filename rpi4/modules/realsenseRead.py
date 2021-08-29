#!/usr/bin/env python3
""" EMAR MINI realsense D415 Reader Module

The realsense D415 Reader module reads frames from the
RealSense D415 camera and publishes them to the camera stream.

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

import pyrealsense2 as rs

import numpy as np

from datetime import datetime
from threading import Thread

from modules.helpers import helpers
from modules.model import model
from modules.realsense import realsense

class realsenseRead(Thread):
    """ realsense D415 Reader Class

    The realsense D415 Reader module reads frames from the
    RealSense D415 camera and publishes them to the camera stream.
    """

    def __init__(self):
        """ Initializes the class. """

        self.helpers = helpers("realsense D415 Reader")
        super(realsenseRead, self).__init__()
        self.ip = self.helpers.get_ip_addr()
        self.port = self.helpers.credentials["socket"]["port"]

        self.helpers.logger.info(
            "realsense D415 Reader Class initialization complete.")

    def run(self):
        """ Runs the module. """

        self.colorizer = rs.colorizer()

        # OpenCV fonts
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.black = (0, 0, 0)
        self.green = (0, 255, 0)
        self.white = (255, 255, 255)

        # Starts the realsense module
        self.realsense = realsense()
        # Connects to the realsense camera
        self.profile = self.realsense.connect()

        # Sets up the object detection model
        self.model = model()

        time1 = 0
        time2 = 0
        fc = 0
        dc = 0
        fps = ""
        dfps = ""

        # Starts the socket server
        soc = self.socket.connect()

        try:
            while True:
                time.sleep(0.05)
                t1 = time.perf_counter()

                # Wait for depth and color frames
                frames = self.realsense.pipeline.wait_for_frames()

                # Get color frames
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                # Get infrared frames
                #ir1_frame = frames.get_infrared_frame(1)
                #ir2_frame = frames.get_infrared_frame(2)

                if not depth_frame or not color_frame:
                #if not not ir1_frame or not ir2_frame:
                    self.helpers.logger.info("realsense D415 streams not ready, continuing.")
                    continue

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                #ir1_image = np.asanyarray(self.colorizer.colorize(ir1_frame).get_data())
                #ir2_image = np.asanyarray(self.colorizer.colorize(ir2_frame).get_data())
                colorized_depth = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())

                # Sets the blob and gets the detections from forward pass
                self.model.setBlob(color_image)
                detections = self.model.forwardPass()

                # Gets width, height and crop value for frame
                width, height = self.model.getDims(color_image)

                # Writes header to frame
                cv2.putText(color_image, "EMAR Mini Color Stream", (30,50), self.font,
                            0.7, self.black, 2, cv2.LINE_AA)

                # Writes date to frame
                cv2.putText(color_image, str(datetime.now()), (30,80), self.font,
                            0.5, self.black, 2, cv2.LINE_AA)

                # Writes header to frame
                cv2.putText(colorized_depth, "EMAR Mini Depth Stream", (30,50), self.font,
                            0.7, self.white, 2, cv2.LINE_AA)

                # Writes date to frame
                cv2.putText(colorized_depth, str(datetime.now()), (30,80), self.font,
                            0.5, self.white, 2, cv2.LINE_AA)

                for i in range(detections.shape[2]):
                    # Detection FPS
                    if i == 0:
                        dc += 1

                    # Gets and checks confidence of detection
                    confidence = detections[0, 0, i, 2]
                    if (confidence <= self.helpers.confs["MobileNetSSD"]["threshold"]):
                        continue

                    # Gets class of detection
                    class_id = int(detections[0, 0, i, 1])

                    # Gets bounding box of detection
                    box_blx = int(detections[0, 0, i, 3] * width)
                    box_bly = int(detections[0, 0, i, 4] * height)
                    box_trx = int(detections[0, 0, i, 5] * width)
                    box_try = int(detections[0, 0, i, 6] * height)

                    # Gets the meters from the depth frame
                    meters = depth_frame.as_depth_frame().get_distance(box_blx+int((box_trx-box_blx)/2),
                                                                       box_bly+int((box_try-box_bly)/2))

                    # Prepares label text
                    if meters != 0.00:
                        label_text = self.helpers.confs["MobileNetSSD"]["classes"][int(class_id)] \
                                        + " (" + str(confidence) + "%)"+ " {:.2f}".format(meters) + "m"
                    else:
                        label_text = self.helpers.confs["MobileNetSSD"]["classes"][int(class_id)] \
                                        + " (" + str(confidence) + "%)"

                    cv2.rectangle(color_image, (box_blx, box_bly),
                                  (box_trx, box_try), self.green, 1)

                    # Positions and writes the label
                    label_size = cv2.getTextSize(label_text, self.font, 0.5, 1)[0]
                    label_left = box_blx

                    label_top = box_bly - label_size[1]
                    if (label_top < 1):
                        label_top = 1

                    label_bottom = label_top + label_size[1]

                    cv2.putText(color_image, label_text, (label_left, label_bottom),
                                self.font, 0.5, self.green, 1)

                # Writes FPS and Detection FPS
                cv2.putText(color_image, fps, (width-170, 50), self.font, 0.5,
                            self.black, 1, cv2.LINE_AA)
                cv2.putText(color_image, dfps, (width-170, 65), self.font, 0.5,
                            self.black, 1, cv2.LINE_AA)

                # Combine the color_image and colorized_depth frames together:
                frame = np.hstack((color_image, colorized_depth))
                # Combine the ir1_image and ir2_image frames together:
                #frame = np.hstack((ir1_image, ir2_image))

                # Streams the modified frame to the socket server
                encoded, buffer = cv2.imencode('.jpg', frame)
                soc.send(base64.b64encode(buffer))

                # FPS calculation
                fc += 1
                if fc >= 15:
                    fps = "Stream: {:.1f} FPS".format(time1/15)
                    dfps = "Detection: {:.1f} FPS".format(dc/time2)
                    fc = 0
                    dc = 0
                    time1 = 0
                    time2 = 0
                t2 = time.perf_counter()
                elapsedTime = t2-t1
                time1 += 1/elapsedTime
                time2 += elapsedTime
                time.sleep(0.05)

        finally:
            # Stop streaming
            self.realsense.pipeline.stop()
