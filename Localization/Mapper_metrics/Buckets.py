from Localization.Mapper_metrics.Metric import Metric
from Localization import Utilities
from Localization import Mapper


class Buckets(Metric):
    """
    Room buckets which fill by 1 for every room in mac:rssi pair
    Normalize is each bucket divided by number of MACS appearing in that room

    Returns int or list
    """

    def __init__(self, m: Mapper, normalize: bool = False):
        if normalize:
            super().__init__("Normalized Buckets")
        else:
            super().__init__("Buckets")
        self.__m = m
        self.__normalize = normalize

    def decide(self, jsondata):
        global_data = self.__m.data
        global_rooms = self.__m.rooms

        rooms_buckets = []
        for i in range(Utilities.ROOMS):
            rooms_buckets.append(0)
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = Utilities.convert_rssi(rssi)
            if mac in global_data:
                if rssi in global_data[mac]:
                    for room in global_data[mac][rssi]:
                        rooms_buckets[room] += 1

        if self.__normalize:
            for i in range(Utilities.ROOMS):
                if i in global_rooms:
                    rooms_buckets[i] = (rooms_buckets[i] / len(global_rooms[i]))

        room = Utilities.mapper_metrics_result(rooms_buckets)

        return room
