import Localization
from Localization import Mapper
import logging

logger = logging.getLogger('Localization.Localization')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

m = Mapper.Mapper(read_filename="/tmp/test.csv", write_filename="/tmp/test.csv")
m.remove_room(3)
server = Localization.Server(m)
server.add_write_server()
server.looper()