from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
import keras
import numpy as np

from Localization import Utilities
from os import path
import csv


class Thinker:
    """ Class handling AI """

    def __init__(self, read_macs=None, read_filename=None, write_macs=None, write_filename=None, model_file=None):
        self.__data = []
        self.__macs = []
        self.__read_macs = read_macs
        self.__read_filename = read_filename
        self.__write_macs = write_macs
        self.__write_filename = write_filename
        self.__hot_macs = False
        if self.__read_filename and self.__read_macs:
            self.__load()
            if self.__read_macs == self.__write_macs:
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

    def __load(self):
        if not self.__read_filename:
            return
        self.__load_macs()
        if path.exists(self.__read_filename):
            print("LOADING ENTRIES FROM %s" % self.__read_filename)
            with open(self.__read_filename, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    room = int(row[0])
                    data = {}
                    i = 0
                    for mac in self.__macs:
                        i += 1
                        rssi = 0
                        if i < len(row) and row[i] != '':
                            rssi = int(row[i])
                        data[mac] = rssi
                    self.__write_map(data=data, room=room)

    def __load_macs(self):
        if not self.__read_macs:
            return
        if path.exists(self.__read_macs):
            print("LOADING MACS FROM %s" % self.__read_macs)
            with open(self.__read_macs, 'r') as macfile:
                macslist = macfile.read().split('\n')
                for mac in macslist:
                    if mac != '':
                        self.__add_to_macs(mac)

    def train(self, outfile):
        model = Sequential()
        # model.add(Dense(2*len(self.__macs), input_dim=len(self.__macs), activation='relu'))
        model.add(Dense(3*len(self.__macs), input_dim=len(self.__macs), activation='relu'))
        model.add(Dense(3*Utilities.ROOMS, activation='relu'))
        model.add(Dense(2*Utilities.ROOMS, activation='relu'))
        # model.add(Dense(Utilities.ROOMS, activation='relu'))
        model.add(Dense(Utilities.ROOMS, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        dataset = []
        rows = 0
        with open(self.__read_filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                rows += 1
                room = int(row[0])
                i = 0
                arr = [room]
                for mac in self.__macs:
                    i += 1
                    rssi = 0
                    if i < len(row) and row[i] != '':
                        rssi = int(row[i])
                    arr.append(rssi)
                dataset.append(arr)
        dataset = np.array(dataset)

        x = dataset[:, 1:]
        y = dataset[:, 0]
        y = to_categorical(y, num_classes=Utilities.ROOMS)

        model.fit(x, y, epochs=1500, batch_size=rows, validation_split=0.5)
        print("EXPORTING MODEL %s" % outfile)
        model.save(outfile)

    def load_from_mapper(self, m):
        def get_recurr(data, rec_data):
            if len(rec_data) == 0:
                self.__write_map(data=data, room=room)
                self.__save(data, room)
                return
            mac = list(rec_data)[0]
            rec_data_tmp = rec_data.copy()
            new_data = data.copy()
            del rec_data_tmp[mac]
            if len(rec_data[mac]) == 0:
                new_data[mac] = 0
                get_recurr(new_data, rec_data_tmp)
            for rssi in rec_data[mac]:
                new_data[mac] = rssi
                get_recurr(new_data, rec_data_tmp)

        rooms = set()
        for mac in m.data:
            self.__add_to_macs(mac)
            for rssi in m.data[mac]:
                for room in m.data[mac][rssi]:
                    rooms.add(room)
        for room in rooms:
            room_data = {}
            for mac in m.data:
                room_data[mac] = []
                for rssi in m.data[mac]:
                    if room in m.data[mac][rssi]:
                        rssi = Utilities.convert_rssi(rssi)
                        if rssi not in room_data[mac]:
                            room_data[mac].append(rssi)
            get_recurr({}, room_data)
