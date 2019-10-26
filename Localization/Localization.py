""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)


class LocalizationServer(object):
    """ Class handling requests """

    def __init__(self, port=2000):

        self.loop = asyncio.get_event_loop()
        listen = self.loop.create_datagram_endpoint(LocalizationHandler, local_addr=('127.0.0.1', port))
        self. loop.run_until_complete(listen)
        self.loop.run_forever()

        _LOGGER.debug("Server up at port %s", port)


class LocalizationHandler:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode().strip('\n')
        _LOGGER.debug('Received from %s message "%s"', addr, message)
        try:
            _LOGGER.debug(json.loads(data))
        except Exception as e:
            _LOGGER.error("NO JSON: %s", e)
        # print('Send %r to %s' % (message, addr))
        # self.transport.sendto(data, addr)
