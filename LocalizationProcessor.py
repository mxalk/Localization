""" Server analyzing json MAC:RSSI to determine location """
import socket
import json
import logging

_LOGGER = logging.getLogger(__name__)

class LocalizationProcessor(object):
    """ Class handling requests """

    def _init_(self, host='localhost', port=2000, bufferSize  = 1024):
        self.bufferSize = bufferSize
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((host, port))
        _LOGGER.debug("Server up, at %s %s", host, port)
        self.run()

    def run(self):
        while (True):
            data = self.UDPServerSocket.recvfrom(self.bufferSize)
            try:
                self.handle(data)
            except:
                print("Exception")

    def handle(data):
        data = json.loads(data)
        print(data)
