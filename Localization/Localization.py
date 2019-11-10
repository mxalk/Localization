""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

ROOMS = 8
BUCKETS = 50
RSSI_OFFSET = 25

BUCKET_SIZE = (100-RSSI_OFFSET)/BUCKETS
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

        m.print()
        room = m.read(jsondata)
        global ITER
        print("%5d) ROOM: %d" % (ITER, room))
        ITER+=1

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
        room = 0
        for mac in jsondata:
            if mac == "#":
                room = int(jsondata[mac])
                continue
            rssi = jsondata[mac]
            rssi = abs(int(rssi))
            m.write_map(mac, rssi, room)

        m.print()
        global ITER
        print("%5d) WRITE: %d" % (ITER, room))
        ITER+=1


class Mapper:
    """ Class handling data """

    def __init__(self):
        self.data = {}

    def write_map(self, mac, rssi, data):
        rssi = int(rssi//BUCKET_SIZE)-RSSI_OFFSET
        if mac not in self.data:
            self.data[mac] = {}
        if rssi not in self.data[mac]:
            self.data[mac][rssi] = []
        if data not in self.data[mac][rssi]:
            self.data[mac][rssi].append(data)
        self.save()

    def read(self, jsondata):
        global_data = m.data
        all_rooms = []
        for i in range(ROOMS):
            all_rooms.append(0)
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = int(abs(int(rssi))//BUCKET_SIZE)
            if mac in global_data:
                if rssi in global_data[mac]:
                    for room in self.data[mac][rssi]:
                        all_rooms[room] += 1
        room = all_rooms.index(max(all_rooms))
        for i in range(ROOMS):
            print("%d: %d" % (i, all_rooms[i]))
        print()
        if all_rooms[room] == 0:
            return -1
        return room
        # rooms = []
        # rooms.append(m.data[mac][rssi])
        # if len(rooms) == 0:
        #     return [0]
        # return rooms
        # return 0

    def print(self):
        print("%17s" % ("MAC \\ RSSI"), end="")
        for bucket in range(BUCKETS):
            print("%4s" % (str(int(bucket*BUCKET_SIZE)+RSSI_OFFSET)), end="")
        print('')
        for mac in self.data:
            print("%17s" % (mac), end="")
            for bucket in range(BUCKETS):
                data = ""
                if bucket in self.data[mac]:
                    rooms = self.data[mac][bucket]
                    acc = 0
                    for item in rooms:
                        acc += 2**(item-1)
                    data = acc
                print("%4s" % (data), end="")
            print('')
        print('')

    def save(self, file):
        string = "MAC"
        for bucket in range(BUCKETS):
            string += ";"+str(int(bucket*BUCKET_SIZE)+RSSI_OFFSET)
        string += '\n'
        for mac in self.data:
            string += mac
            for bucket in range(BUCKETS):
                string += ';'
                if bucket in self.data[mac]:
                    string += str(self.data[mac][bucket])
            string += '\n'
        print(string)


m = Mapper()


class Server:
    """ Class initializing server """

    default_port = 2000

    def __init__(self, port=default_port):
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