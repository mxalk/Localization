import Localization
import logging

logger = logging.getLogger('Localization.Localization')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

server = Localization.Server(2000, read_filename="/tmp/test.csv", write_filename="/tmp/test.csv")
# server = Localization.Server(2000, read_filename="/tmp/test.csv")
server.add_write_server(2001)
server.looper()
# server.