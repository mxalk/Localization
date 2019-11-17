from Localization.Mapper_metrics.Metric import Metric
from Localization import Utilities
from Localization import Mapper


class UniqueBuckets(Metric):
    """
    Room buckets which fill by 1 if only one room corresponds to the mac:rssi pair

    Returns int or list
    """

    def __init__(self, m: Mapper):
        super().__init__("Unique Buckets")
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
                        if len(global_data[mac][rssi]) == 1:
                            rooms_buckets[room] += 1

        room = Utilities.mapper_metrics_result(rooms_buckets)

        return room
