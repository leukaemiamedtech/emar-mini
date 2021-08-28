""" Socket Server class.

Socket server functions for the camera stream.

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

import zmq, base64

import numpy as np

from modules.helpers import helpers

class socket():

    def __init__(self):
        """ Socket Server Class

        Socket server functions for the camera stream.
        """

        self.helpers = helpers("Socket", False)

        self.ip = self.helpers.get_ip_addr()
        self.port = self.helpers.credentials["socket"]["port"]

        self.helpers.logger.info(
                            "Socket Helper Class initialization complete.")

    def connect(self):
        """ Connects to the local Socket. """

        try:
            soc = zmq.Context().socket(zmq.PUB)
            soc.connect("tcp://"+self.ip+":"+str(self.port))
            self.helpers.logger.info(
                "Started & connected to socket server: tcp://" \
                +self.ip+":"+str(self.port))
            return soc
        except:
            self.helpers.logger.info(
                "Failed to connect to socket server: tcp://" \
                + self.ip+":"+str(self.port))

    def subscribe(self):
        """ Subscirbes to the server. """

        try:
            context = zmq.Context()
            rsoc = context.socket(zmq.SUB)
            rsoc.setsockopt(zmq.CONFLATE, 1)
            rsoc.bind("tcp://"+self.ip+":"+str(self.port))
            rsoc.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
            self.helpers.logger.info(
                "Subscribed to socket: tcp://" \
                +self.ip+":"+str(self.port))
            return rsoc
        except:
            self.helpers.logger.info(
                "Failed to connect to tcp://" \
                +self.ip+":"+str(self.port))
