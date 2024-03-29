import time
from test_base import *


class ClientTestCase(BaseTestCase):
    def test_configuration(self):
        self.assertTrue(self.client.configuration())

    def test_register(self):
        self.client.register()

    def test_request(self):
        self.client.request(self.method_id, data=self.data)

    def test_response(self):
        self.assertEqual(self.client.callback_message(SOMEIP.Message_Type.RESPONSE.value, self.method_id, self.data), None)

    def test_on_message(self):
        self.client.on_message(self.method_id)

        count = self.client.counter
        while True:
            self.client.request(self.method_id, self.data)
            time.sleep(3)
            if self.client.counter > count:
                break
        self.assertTrue(self.client.counter > count)

    def test_on_event(self):
        for event_id in self.event_ids:
            self.client.on_event(event_id)
        count = self.client.counter + len(self.event_ids)
        while True:
            time.sleep(1)
            for event_id in self.event_ids:
                self.service.notify(event_id, self.data)
                time.sleep(3)
            if self.client.counter > count:
                break
        self.assertTrue(self.client.counter > count)

    @unittest.skip("Skipping as it indicates service verse client")
    def test_offer(self):
        self.client.offer(self.event_ids)

    def test_notify(self):
        for event_id in self.event_ids:
            with self.assertRaises(UserWarning):
                self.client.notify(event_id, self.data)


if __name__ == '__main__':
    unittest.main()
