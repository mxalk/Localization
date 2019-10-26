""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

class Server:
    """ Class initializing server """

    def __init__(self, port=2000):

        self.loop = asyncio.get_event_loop()
        listen = self.loop.create_datagram_endpoint(Handler, local_addr=('127.0.0.1', port))
        self. loop.run_until_complete(listen)
        self.loop.run_forever()

        _LOGGER.debug("Server up at port %s", port)


class Handler:
    """ Class handling requests """

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode().strip('\n')
        _LOGGER.debug('Received from %s message "%s"', addr, message)
        try:
            jsondata = json.loads(data)
        except Exception as e:
            _LOGGER.error("NO JSON: %s", e)
            return
        # print('Send %r to %s' % (message, addr))
        # self.transport.sendto(data, addr)

class Mapper:
    """ Class handling data """

    def __init__(self):
        self.data = {}

    def write_map(self, mac, rssi, data):
        if mac not in self.data:
            self.data[mac] = {}
        if rssi not in self.data[mac]:
            self.data[mac] = []
        if data not in self.data[mac][rssi]:
            self.data[mac][rssi].append(data)

    def write_json_map(self, dict_map, data):
        for mac, rssi in dict_map:
            self.add_map(mac, rssi, data)

    def read(self, dict_map):
        data = []
        for mac, rssi in dict_map:
            data.append(self.data[mac][rssi])

