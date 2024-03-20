import os, sys
import unittest
from typing import Tuple, List
import tracemalloc
from someip_adapter.vsomeip import SOMEIP


class SOMEIP_Test(SOMEIP):
    def __init__(self, name: str, id: int, instance: int, configuration: dict, version: Tuple[int, int] = (0x0A, 0x01)):
        super().__init__(name, id, instance, configuration, version)
        self.counter = 0

    def callback_message(self, type: int, id: int, data: bytearray) -> bytearray:
        self.counter = self.counter + 1
        return super().callback_message(type, id, data)

def setup_client(index: int = 0) -> SOMEIP_Test:
    configuration = SOMEIP.configuration()

    client_name = "client_example" + f"_{index}"
    service_id = 0x1234 + index
    service_instance = 0x5678
    service_port = 30509 + index

    configuration["applications"].append({'name': client_name, 'id': 0x2222 + index})
    configuration["clients"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})

    return SOMEIP_Test(client_name, service_id, service_instance, configuration)


def setup_service(index: int = 0) -> SOMEIP_Test:
    configuration = SOMEIP.configuration()

    service_name = "service_example" + f"_{index}"
    service_id = 0x1234 + index
    service_instance = 0x5678
    service_port = 30509 + index

    configuration["applications"].append({'name': service_name, 'id': 0x1111 + index})
    configuration["services"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})

    return SOMEIP_Test(service_name, service_id, service_instance, configuration)


class BaseTestCase(unittest.TestCase):

    client = None
    service = None
    service_extra = None

    data = bytearray([0x1, 0x2, 0x3])
    method_id = 0x9002
    event_ids = [0x8778]

    @classmethod
    def setUpClass(cls):
        tracemalloc.start()

        cls.service = setup_service()
        cls.service_extra = setup_service(1)
        cls.client = setup_client()

        cls.service.create()
        cls.service_extra.create()
        cls.client.create()

        cls.service_extra.offer()
        cls.service_extra.start()

        cls.service.offer()
        cls.service.on_message(cls.method_id)
        cls.service.offer(events=cls.event_ids)
        cls.service.start()

        cls.client.start()
        cls.client.register()

    @classmethod
    def tearDownClass(cls):
        cls.service.stop()
        cls.client.stop()
