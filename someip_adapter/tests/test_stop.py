import time
from .test_base import *


class ClientTestCase(unittest.TestCase):

    def test_stop(self):
        client = setup_client(99)
        client.start()
        client.register()
        time.sleep(10)
        client.stop()
        time.sleep(10)

