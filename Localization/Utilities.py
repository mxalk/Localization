import math

ROOMS = 8
MAX_RSSI = 100
# LOG_BASE = 1.5
BUCKETS = 100


def convert_rssi(rssi):
    # return abs(int(rssi))
    rssi_new = round((abs(int(rssi))-20)/4)
    # rssi_new = round((math.log(abs(int(rssi))-20, LOG_BASE)))
    # print(str(rssi) + " --> " + str(abs(int(rssi))) + " --> " + str(abs(int(rssi))-20) + " --> " + str(rssi_new))
    # global BUCKETS
    # BUCKETS = math.ceil(math.log(MAX_RSSI, LOG_BASE))
    return rssi_new

def mapper_metrics_result(rooms_buckets: list):
    results = []
    max_item = rooms_buckets[0]
    for i in range(ROOMS):
        score = rooms_buckets[i]
        if score > max_item:
            max_item = score
            results = [i]
        elif score == max_item:
            results.append(i)
    room = results
    if len(results) == 1:
        room = results[0]
    return room