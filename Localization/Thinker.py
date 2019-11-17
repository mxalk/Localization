
class Thinker:
    """ Class handling AI """

    def __init__(self, read_macs=None, read_filename=None, write_macs=None, write_filename=None, model_file=None):
        self.__data = []
        self.__macs = []
        self.__write_macs = write_macs
        self.__write_filename = write_filename
        self.__hot_macs = False

    def write(self, jsondata):
        room = 0
        for mac in jsondata:
            if mac == "#":
                room = int(jsondata[mac])
                break
        if room == 0:
            return 0
        del jsondata['#']
        data = {}
        for mac in jsondata:
            self.__add_to_macs(mac)
            rssi = jsondata[mac]
            rssi = Utilities.convert_rssi(rssi)
            data[mac] = rssi
        print(data)
        if self.__write_map(data=data, room=room):
            self.__save(data, room)
        return room

    def __write_map(self, data, room):
        entry = [room]
        for mac in self.__macs:
            if mac in data:
                entry.append(data[mac])
            else:
                entry.append(0)
        if entry not in self.__data:
            self.__data.append(entry)
            return True
        return False

    def __add_to_macs(self, mac):
        if mac not in self.__macs:
            self.__hot_macs = True
            self.__macs.append(mac)

    def __save(self, data, room):
        if not self.__write_filename or not self.__write_macs:
            return
        if self.__hot_macs:
            print("WRITING MACS TO %s" % self.__write_macs)
            with open(self.__write_macs, 'w') as macsfile:
                for mac in self.__macs:
                    macsfile.write(mac + '\n')
                self.__hot_macs = False
        print("APPENDING ENTRIES TO %s" % self.__write_filename)
        with open(self.__write_filename, 'a+') as csvfile:
            csv_writer = csv.writer(csvfile)
            entry = [room]
            for mac in self.__macs:
                if mac in data:
                    entry.append(str(data[mac]))
                else:
                    entry.append('')
            csv_writer.writerow(entry)
