import math

ROOMS = 8
MAX_RSSI = 100
LOG_BASE = 1.4
BUCKETS = 100


class Mapper:
    """ Class handling data """

    def __init__(self, read_filename=None, write_filename=None):
        self.data = {}
        self.rooms = {}
        if read_filename:
            self.load(read_filename)
        self.write_filename = write_filename

    def write(self, jsondata):
        room = 0
        for mac in jsondata:
            if mac == "#":
                room = int(jsondata[mac])
                continue
            rssi = jsondata[mac]
            rssi = convert_rssi(rssi)
            if self.write_map(mac, rssi, room):
                self.save()
        return room

    def write_map(self, mac, rssi, data):
        if mac not in self.data:
            self.data[mac] = {}
        if rssi not in self.data[mac]:
            self.data[mac][rssi] = []
        if data not in self.data[mac][rssi]:
            self.data[mac][rssi].append(data)
            print("New entry: %s %d %d" % (mac, rssi, data))
            if data not in self.rooms:
                self.rooms[data] = []
            if mac not in self.rooms[data]:
                self.rooms[data].append(mac)
            return True
        return False

    def read(self, jsondata):
        global_data = self.data
        all_rooms1 = []
        all_rooms2 = []
        all_rooms3 = []
        for i in range(ROOMS):
            all_rooms1.append(0)
            all_rooms2.append(0)
            all_rooms3.append(0)
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = convert_rssi(rssi)
            if mac in global_data:
                if rssi in global_data[mac]:
                    for room in self.data[mac][rssi]:
                        all_rooms1[room] += 1
                        all_rooms2[room] += 1 / len(self.data[mac][rssi])
                        if len(self.data[mac][rssi]) == 1:
                            all_rooms3[room] += 1
        results1 = []
        for i in range(ROOMS):
            if i not in self.rooms:
                results1.append(0)
                continue
            results1.append(all_rooms1[i] * 100 / len(self.rooms[i]))
        room1 = results1.index(max(results1))

        results2 = []
        max_item = all_rooms2[0]
        for i in range(ROOMS):
            score = all_rooms2[i]
            if score > max_item:
                max_item = score
                results2 = [i]
            elif score == max_item:
                results2.append(i)
        room2 = results2
        if len(results2) == 1:
            room2 = results2[0]

        results3 = []
        room3 = all_rooms3.index(max(all_rooms3))

        for i in range(0, ROOMS):
            if i not in self.rooms:
                continue
            print("%d: %4.1f%% confidence (%d/%d)  |            %4.1f  |  %4.1f" % (
                i, results1[i], all_rooms1[i], len(self.rooms[i]), all_rooms2[i], all_rooms3[i]))
        print("ROOMS:\t\t      %d    |%17s |    %s" % (room1, str(room2), str(room3)))

        results = []
        for i in range(0, ROOMS):
            results.append(0)
        results[room1] += 1
        if type(room2) == list:
            for room in room2:
                results[room] += 1
        else:
            results[room2] += 2
        results[room3] += 1
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

    def print_hightlight(self, jsondata):
        string = "\n\n\n----------------------------------------------------------------------------------------------" \
                 "----------------------------------------------------------------------------------------------\n"
        for mac in self.data:
            string += mac
            string_extra = ''
            found_room = 0
            for rssi in range(BUCKETS):
                string_extra += ','
                if rssi in self.data[mac]:
                    rooms = self.data[mac][rssi]
                    acc = 0
                    for room in rooms:
                        acc += 2 ** (room - 1)
                    if mac in jsondata and rssi == convert_rssi(jsondata[mac]):
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
            for rssi in range(BUCKETS):
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
        print("LOADING DATA")
        f = open(filename, 'r').read().split('\n')
        for row in f[:-1]:
            row_data = row.split(',')
            mac = row_data[0]
            for rssi in range(1, BUCKETS):
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


def convert_rssi(rssi):
    return abs(int(rssi))
    rssi = int(math.log(abs(int(rssi)), LOG_BASE))
    global BUCKETS
    BUCKETS = math.ceil(math.log(MAX_RSSI, LOG_BASE))
    return rssi
