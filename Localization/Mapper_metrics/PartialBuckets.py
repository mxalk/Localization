from Localization.Mapper_metrics.Metric import Metric
from Localization import Utilities
from Localization import Mapper


class PartialBuckets(Metric):
    """
    Room buckets which fill by 1 / (number of rooms) for each value in mac:rssi pair
    e.g. 2 rooms give 0.5 to each bucket, 3 rooms amount to 0.33 each

    Returns int or list
    """

    def __init__(self, m: Mapper):
        super().__init__("Partial Buckets")
        self.__m = m

    def decide(self, jsondata):
        global_data = self.__m.data

        rooms_buckets = []
        for i in range(Utilities.ROOMS):
            rooms_buckets.append(0)
        for mac in jsondata:
            rssi = jsondata[mac]
            rssi = Utilities.convert_rssi(rssi)
            if mac in global_data:
                if rssi in global_data[mac]:
                    for room in global_data[mac][rssi]:
                        rooms_buckets[room] += 1 / len(global_data[mac][rssi])

        room = Utilities.mapper_metrics_result(rooms_buckets)

        return room
