import os, sys
import unittest
from typing import Tuple, List
import tracemalloc
from someip_adapter.vsomeip import SOMEIP

is_windows = sys.platform.startswith('win')


class SOMEIP_Test(SOMEIP):
    def __init__(self, name: str, id: int, instance: int, configuration: dict, version: Tuple[int, int] = (0x0A, 0x01)):
        super().__init__(name, id, instance, configuration, version)
        self.counter = 0

    def callback(self, type: int, id: int, data: bytearray) -> bytearray:
        self.counter = self.counter + 1
        print(f"{type} -> id: {id}, data: {data}")
        return super().callback(type, id, data)


def setup_client(index: int = 0) -> SOMEIP_Test:
    configuration = SOMEIP._configuration_template()

    client_name = "client_example" + f"_{index}"
    service_id = 0x1234
    service_instance = 0x5678
    service_port = 30509

    configuration["applications"].append({'name': client_name, 'id': 0x2222 + index})
    configuration["clients"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})

    return SOMEIP_Test(client_name, service_id, service_instance, configuration)


def setup_service() -> SOMEIP_Test:
    configuration = SOMEIP._configuration_template()

    service_name = "service_example"
    service_id = 0x1234
    service_instance = 0x5678
    service_port = 30509

    configuration["applications"].append({'name': service_name, 'id': 0x1111})
    configuration["services"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})

    # this service will act as the router
    configuration["routing"] = service_name

    return SOMEIP_Test(service_name, service_id, service_instance, configuration)


class BaseTestCase(unittest.TestCase):

    client = None
    service = None

    data = bytearray([0x1, 0x2, 0x3])
    method_id = 0x9002
    event_ids = [0x8778]

    @classmethod
    def setUpClass(cls):
        tracemalloc.start()

        cls.service = setup_service()
        cls.client = setup_client()

    @classmethod
    def tearDownClass(cls):
        cls.service.stop()
        cls.client.stop()
