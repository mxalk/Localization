import math

ROOMS = 8
MAX_RSSI = 100
LOG_BASE = 1.4
BUCKETS = 100


def convert_rssi(rssi):
    return abs(int(rssi))
    rssi = int(math.log(abs(int(rssi)), LOG_BASE))
    global BUCKETS
    BUCKETS = math.ceil(math.log(MAX_RSSI, LOG_BASE))
    return rssi