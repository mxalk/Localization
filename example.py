import Localization
from Localization import Mapper
from Localization import Thinker
import logging

logger = logging.getLogger('Localization.Localization')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)


def training():
    t = Thinker.Thinker(
        read_macs="/tmp/thinker_macs.csv", read_filename="/tmp/thinker.csv",
        write_macs="/tmp/thinker_macs.csv", write_filename="/tmp/thinker.csv"
    )
    t.train(outfile="/tmp/trained")

def server_thinker():
    t = Thinker.Thinker(
        read_macs="/tmp/thinker_macs.csv", read_filename="/tmp/thinker.csv",
        write_macs="/tmp/thinker_macs.csv", write_filename="/tmp/thinker.csv",
        model_file="/tmp/trained"
    )
    s = Localization.Server(t)
    s.add_write_server()
    s.looper()

def server_mapper():
    m = Mapper.Mapper(read_filename="/tmp/mapper.csv", write_filename="/tmp/mapper.csv")
    s = Localization.Server(m)
    s.add_write_server()
    s.looper()

# t.load_from_mapper(m)
training()
server_thinker()
# server_mapper()
