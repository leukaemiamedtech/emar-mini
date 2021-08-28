""" AI Model class.

Provides methods for interacting with ai models.

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

import cv2


from modules.helpers import helpers

class model():
    """ AI Model class.

    Provides methods for interacting with ai models.
    """

    def __init__(self):
        """ Initializes the model class. """

        self.helpers = helpers("model", False)

        self.net = cv2.dnn.readNet(
            self.helpers.confs["MobileNetSSD"]["xml"],
            self.helpers.confs["MobileNetSSD"]["bin"])
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

        self.imsize = self.helpers.confs["MobileNetSSD"]["size"]

        self.helpers.logger.info("Model class initialization complete.")

    def getDims(self, frame):
        """ Gets the width and height of frame """

        height = frame.shape[0]
        width = frame.shape[1]

        return width, height

    def setBlob(self, frame):
        """ Gets a blob from the color frame """

        blob = cv2.dnn.blobFromImage(frame, self.helpers.confs["MobileNetSSD"]["inScaleFactor"],
                                    size=(self.imsize, self.imsize),
                                    mean=(self.helpers.confs["MobileNetSSD"]["meanVal"],
                                        self.helpers.confs["MobileNetSSD"]["meanVal"],
                                        self.helpers.confs["MobileNetSSD"]["meanVal"]),
                                    swapRB=False, crop=False)

        self.net.setInput(blob)

    def getCrop(self, width, height):
        """ Gets the crop size """

        ratio = self.imsize / float(self.imsize)

        if width / float(height) > ratio:
            crop = (int(height * ratio), height)
        else:
            crop = (width, int(width / ratio))

        return crop

    def forwardPass(self):
        """ Gets a blob from the color frame """

        out = self.net.forward()

        return out