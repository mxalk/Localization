
ROOMS = 8


class Mapper:
    """ Class handling data """

    def __init__(self, read_filename=None, write_filename=None):
        self.data = {}
        self.rooms = {}
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
            if data not in self.rooms:
                self.rooms[data] = []
            if mac not in self.rooms[data]:
                self.rooms[data].append(mac)
            return True
        return False

    def read(self, jsondata):
        global_data = self.data
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
        results = []
        for i in range(ROOMS):
            if i not in self.rooms:
                results.append(0)
                continue
            results.append(all_rooms[i]*100/len(self.rooms[i]))
            print("%d: %3d%% confidence (%d/%d)" % (i, results[i], all_rooms[i], len(self.rooms[i])))
        room = results.index(max(results))
        if all_rooms[room] == 0:
            return -1
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
                        acc += 2**(item-1)
                    data = acc
                print("%4s" % data, end="")
            print('')
        print('')

    def save(self):
        if not self.write_filename:
            return
        print("WRITING TO %s" % self.write_filename)
        string = ""
        for mac in self.data:
            string += mac
            for rssi in range(101):
                string += ','
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
            row_data = row.split(',')
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
