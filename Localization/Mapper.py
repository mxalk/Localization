from Localization import Utilities

from Localization.Mapper_metrics import Buckets
from Localization.Mapper_metrics import PartialBuckets
from Localization.Mapper_metrics import UniqueBuckets

import os.path


class Mapper:
    """ Class handling data """

    def __init__(self, read_filename: str = None, write_filename: str = None, metrics="all"):
        self.data = {}
        self.rooms = {}
        if read_filename:
            self.load(read_filename)
        self.write_filename = write_filename

        self.__metrics = []
        if metrics == "all":
            self.__metrics.append(Buckets.Buckets(self))
            self.__metrics.append(Buckets.Buckets(self, normalize=True))
            self.__metrics.append(PartialBuckets.PartialBuckets(self))
            self.__metrics.append(UniqueBuckets.UniqueBuckets(self))
        else:
            metrics = set(metrics)
            for metric in metrics:
                if metric == "buckets":
                    self.__metrics.append(Buckets.Buckets(self))
                elif metric == "normbuckets":
                    self.__metrics.append(Buckets.Buckets(self, normalize=True))
                elif metric == "partialbuckets":
                    self.__metrics.append(PartialBuckets.PartialBuckets(self))
                elif metric == "uniquebuckets":
                    self.__metrics.append(UniqueBuckets.UniqueBuckets(self))
            if len(self.__metrics) == 0:
                self.__metrics.append(Buckets.Buckets(self, normalize=True))


    def write(self, jsondata: dict):
        room = 0
        for mac in jsondata:
            if mac == "#":
                room = int(jsondata[mac])
                break
        if room == 0:
            return 0
        del jsondata["#"]
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = Utilities.convert_rssi(rssi)
            if self.write_map(mac, rssi, room):
                self.save()
        return room

    def write_map(self, mac: str, rssi: int, data: int):
        if mac not in self.data:
            self.data[mac] = {}
        if rssi not in self.data[mac]:
            self.data[mac][rssi] = []
        if data not in self.data[mac][rssi]:
            self.data[mac][rssi].append(data)
            print("New entry: %s %d --> %d" % (mac, rssi, data))
            if data not in self.rooms:
                self.rooms[data] = []
            if mac not in self.rooms[data]:
                self.rooms[data].append(mac)
            return True
        return False

    def read(self, jsondata: dict):
        self.print_highlight(jsondata)

        # for i in range(0, Utilities.ROOMS):
        #     if i not in self.rooms:
        #         continue
        #     print("%d: %4.1f%% confidence (%d/%2d)  |            %4.1f  |  %4.1f" % (
        #         i, results1[i], all_rooms1[i], len(self.rooms[i]), all_rooms2[i], all_rooms3[i]))
        # print("ROOMS:\t\t      %d     |%17s |    %s" % (room1, str(room2), str(room3)))

        print(jsondata)
        results = []
        for i in range(0, Utilities.ROOMS):
            results.append(0)
        for metric in self.__metrics:
            rooms = metric.decide(jsondata=jsondata)
            print("%30s: %15s" % (metric.get_name() + " reports ", rooms))
            if type(rooms) == list:
                for room in rooms:
                    results[room] += 1
            elif type(rooms) == int:
                results[rooms] += 1
        room = results.index(max(results))

        return room

    def print(self):
        print("%17s" % "MAC \\ RSSI", end="")
        for rssi in range(101):
            print("%4s" % (str(rssi)), end="")
        print('')
        for mac in self.data:
            print("%17s" % mac, end="")
            for rssi in range(101):
                data = ""
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for item in rooms:
                        acc += 2 ** (item - 1)
                    data = acc
                print("%4s" % data, end="")
            print('')
        print('')

    def print_highlight(self, jsondata: dict):
        string = "\n\n\n----------------------------------------------------------------------------------------------" \
                 "----------------------------------------------------------------------------------------------\n"
        for mac in self.data:
            string += mac
            string_extra = ''
            found_room = 0
            for rssi in range(Utilities.BUCKETS):
                string_extra += ','
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for room in rooms:
                        acc += 2 ** (room - 1)
                    if mac in jsondata and rssi == Utilities.convert_rssi(jsondata[mac]):
                        string_extra += u"\u2588"
                        found_room = acc
                    else:
                        string_extra += str(acc)
            string += " (" + str(found_room) + ") "
            string += string_extra
            string += '\n'
        print(string)

    def toCSV(self):
        string = ""
        for mac in self.data:
            string += mac
            for rssi in range(Utilities.BUCKETS):
                string += ','
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for room in rooms:
                        acc += 2 ** (room - 1)
                    string += str(acc)
            string += '\n'
        return string

    def save(self):
        if not self.write_filename:
            return
        print("WRITING TO %s" % self.write_filename)
        string = self.toCSV()
        f = open(self.write_filename, 'w')
        f.write(string)

    def load(self, filename):
        if not os.path.exists(filename):
            return
        print("LOADING DATA")
        f = open(filename, 'r').read().split('\n')
        for row in f:
            if (row == ''):
                continue
            row_data = row.split(',')
            mac = row_data[0]
            for rssi in range(1, Utilities.BUCKETS):
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

    def remove_room(self, room):
        assert (0 < room < Utilities.ROOMS)
        tuples = []
        for mac in self.data:
            for rssi in self.data[mac]:
                if room in self.data[mac][rssi]:
                    if len(self.data[mac][rssi]) == 1:
                        tuples.append((mac, rssi))
                        continue
                    self.data[mac][rssi].remove(room)
        for (mac, rssi) in tuples:
            del self.data[mac][rssi]
        del self.rooms[room]
        print(self.data)
