import time
from test_base import *


class ServiceTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.service.offer()
        cls.service.start()
        cls.service.offer(events=cls.event_ids)

        cls.client.start()
        cls.client.register()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_configuration(self):
        self.assertTrue(self.service.configuration())

    def test_register(self):
        with self.assertRaises(UserWarning):
            self.service.register()

    def test_request(self):
        with self.assertRaises(UserWarning):
            self.service.request(self.method_id, data=self.data)

    def test_response(self):
        self.assertEqual(self.service.callback(SOMEIP.Message_Type.REQUEST.value, self.method_id, self.data), self.data)

    def test_on_message(self):
        # todo: why need a new client, on own test runs fine...
        client = setup_client(1)
        client.start()
        client.register()

        count = self.service.counter
        self.service.on_message(self.method_id)
        while True:
            client.request(self.method_id, self.data)
            time.sleep(3)
            if self.service.counter > count:
                break
        self.assertTrue(self.service.counter > count)

    def test_on_event(self):
        for event_id in self.event_ids:
            self.service.on_event(event_id)

    def test_offer(self):
        self.service.offer(self.event_ids)
        # test can do again?
        self.service.offer(self.event_ids)

    def test_notify(self):
        # todo: why need a new client, on own test runs fine...
        client = setup_client(1)
        client.start()
        client.register()

        event_id = self.event_ids[0]

        count = self.service.counter
        self.client.on_event(event_id)
        while True:
            self.service.notify(event_id, self.data)
            time.sleep(3)
            if self.client.counter > count:
                break


if __name__ == '__main__':
    unittest.main()
