import Localization
from Localization import Mapper
import logging

logger = logging.getLogger('Localization.Localization')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)


def server_mapper():
    m = Mapper.Mapper(read_filename="/tmp/mapper.csv", write_filename="/tmp/mapper.csv")
    s = Localization.Server(m)
    s.add_write_server()
    s.looper()


server_mapper()