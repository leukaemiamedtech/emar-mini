#!/usr/bin/env python3
""" EMAR MINI Realsense D415 Module

The Realsense D415 module provides helper functions for managing the
Realsense D415.

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

import pyrealsense2 as rs

from modules.helpers import helpers

class realsense():

    def __init__(self):
        """ EMAR MINI Realsense D415 Module

        The Realsense D415 module provides helper functions
        for managing the Realsense D415.
        """

        self.helpers = helpers("Realsense D415", False)
        self.helpers.logger.info(
            "Realsense D415 Helper Class initialization complete.")

    def connect(self):
        """ Connects to the Realsense D415 camera. """

        self.pipeline = rs.pipeline()

        config = rs.config()
        #config.enable_stream(
            # rs.stream.infrared, 1, 640, 480,
            # rs.format.y8, 30)

        #config.enable_stream(
            # rs.stream.infrared, 2, 640, 480,
            # rs.format.y8, 30)

        config.enable_stream(
            rs.stream.depth, 640, 480,
            rs.format.z16, 30)

        config.enable_stream(
            rs.stream.color, 640, 480,
            rs.format.bgr8, 30)

        prof = self.pipeline.start(config)

        self.helpers.logger.info(
            "Connected To Realsense D415")

        return prof