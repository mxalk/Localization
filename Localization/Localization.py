""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

# BUCKETS = 50
# RSSI_OFFSET = 0
#
# BUCKET_SIZE = (101-RSSI_OFFSET)/BUCKETS
ITER = 0


class Reader:
    """ Class handling reads """

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # _LOGGER.debug('Received from %s message "%s"', addr, message)
        try:
            jsondata = json.loads(data)[0]
        except Exception as e:
            _LOGGER.error("NO JSON: %s", e)
            return

        m.print_hightlight(jsondata)
        room = m.read(jsondata)
        global ITER
        print("%5d) ROOM: %d" % (ITER, room))
        ITER += 1


class Writer:
    """ Class handling writes """

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # _LOGGER.debug('Received from %s message "%s"', addr, message)
        try:
            jsondata = json.loads(data)[0]
        except Exception as e:
            _LOGGER.error("NO JSON: %s", e)
            return
        room = m.write(jsondata)

        # m.print()
        global ITER
        print("%5d) WRITE: %d" % (ITER, room))
        ITER += 1


class Server:
    """ Class initializing server """

    default_port = 2000

    def __init__(self, mapper, port=default_port):
        if not mapper:
            raise Exception()
        global m
        m = mapper
        self.default_port=port
        self.loop = asyncio.get_event_loop()
        listen = self.loop.create_datagram_endpoint(Reader, local_addr=('0.0.0.0', port))
        self. loop.run_until_complete(listen)
        _LOGGER.debug("Reader up at port %s", port)

    def add_write_server(self, port=default_port+1):
        self.loop = asyncio.get_event_loop()
        listen = self.loop.create_datagram_endpoint(Writer, local_addr=('0.0.0.0', port))
        self. loop.run_until_complete(listen)
        _LOGGER.debug("Writer up at port %s", port)

    def looper(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_forever()