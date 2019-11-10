""" Server analyzing json MAC:RSSI to determine location """
import logging
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

ROOMS = 8
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

        # m.print()
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
            if m.write_map(mac, rssi, room):
                m.save()

        # m.print()
        global ITER
        print("%5d) WRITE: %d" % (ITER, room))
        ITER+=1


class Mapper:
    """ Class handling data """

    def __init__(self, read_filename, write_filename):
        self.data = {}
        if read_filename:
            self.load(read_filename)
        self.write_filename = write_filename

    def write_map(self, mac, rssi, data):
        if mac not in self.data:
            self.data[mac] = {}
        if rssi not in self.data[mac]:
            self.data[mac][rssi] = []
        if data not in self.data[mac][rssi]:
            self.data[mac][rssi].append(data)
            print("New entry: %s %d %d" % (mac, rssi, data))
            return True
        return False

    def read(self, jsondata):
        global_data = m.data
        all_rooms = []
        for i in range(ROOMS+1):
            all_rooms.append(0)
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = abs(int(rssi))
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

    def print(self):
        print("%17s" % ("MAC \\ RSSI"), end="")
        for rssi in range(101):
            print("%4s" % (str(rssi)), end="")
        print('')
        for mac in self.data:
            print("%17s" % (mac), end="")
            for rssi in range(101):
                data = ""
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for item in rooms:
                        acc += 2**(item-1)
                    data = acc
                print("%4s" % (data), end="")
            print('')
        print('')

    def save(self):
        if not self.write_filename:
            return
        print("WRITING TO %s" % (self.write_filename))
        string = ""
        for mac in self.data:
            string += mac
            for rssi in range(101):
                string += ';'
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for room in rooms:
                        acc += 2 ** (room - 1)
                    string += str(acc)
            string += '\n'
        f = open(self.write_filename, 'w')
        f.write(string)

    def load(self, filename):
        print("LOADING DATA")
        f = open(filename, 'r').read().split('\n')
        for row in f[:-1]:
            row_data = row.split(';')
            mac = row_data[0]
            for rssi in range(101):
                rooms = row_data[1:][int(rssi)]
                if rooms == '':
                    continue
                rooms = float(rooms)
                room = 0
                while rooms >= 1:
                    room += 1
                    if rooms % 2 == 1:
                        print("retrieving %s %s %s" % (mac, rssi, room))
                        self.write_map(mac, int(rssi), int(room))
                    rooms = rooms // 2
                # for room in rooms:
                #     print(room)
                #     print("retrieving %s %s %s" % (mac, rssi, room))
                #     self.write_map(mac, int(rssi), int(room))


class Server:
    """ Class initializing server """

    default_port = 2000

    def __init__(self, port=default_port, read_filename=None, write_filename=None):
        global m
        m = Mapper(read_filename, write_filename)

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