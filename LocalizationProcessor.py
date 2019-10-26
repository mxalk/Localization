""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)


class LocalizationProcessor(object):
    """ Class handling requests """

    def _init_(self, port=2000):

        self.loop = asyncio.get_event_loop()
        self.loop.create_datagram_endpoint(self, local_addr=('localhost', port))
        self.loop.run_forever()

        _LOGGER.debug("Server up at port %s", port)


    def connection_made(self, transport):
        self.transport = transport


    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received from %s message %s', message, addr)
        print(json.loads(data))
        # print('Send %r to %s' % (message, addr))
        # self.transport.sendto(data, addr)