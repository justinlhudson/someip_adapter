import time
from threading import Thread
from someip_adapter.vsomeip import SOMEIP


def service_example(index: int = 0):
    configuration = SOMEIP.default()

    service_name = "service_example"
    service_id = 0x1234
    service_instance = 0x5678
    service_port = 30509

    configuration["applications"].append({'name': service_name, 'id': 0x1111})
    configuration["services"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})
    # this service will act as the router
    configuration["routing"] = service_name

    service_events = [0x8778]
    service_method = 0x9002

    def test(type: int, id: int, data: bytearray) -> bytearray:
        print(f"rx: {id}({service_name}), data: {data}")
        if id == service_method:
            someip.notify(service_events[0], data=data)
        return None

    someip = SOMEIP(service_name, service_id, service_instance, configuration)
    someip.offer()
    someip.start()

    someip.on_message(service_method, callback=test)
    someip.offer(events=service_events)

    while True:
        time.sleep(5)


def client_example(index: int = 0):
    configuration = SOMEIP.default()

    client_name = "client_example" + f"_{index}"
    service_id = 0x1234
    service_instance = 0x5678
    service_port = 30509

    configuration["applications"].append({'name': client_name, 'id': 0x2222 + index})
    configuration["clients"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})
    service_method = 0x9002
    service_events = [0x8778]  # 0x8XXX

    def test(type: int, id: int, data: bytearray) -> bytearray:
        print(f"rx: {id}({client_name}), data: {data}")
        return bytearray(data)

    someip = SOMEIP(client_name, service_id, service_instance, configuration)

    someip.on_message(service_method, test)
    for service_event in service_events:
        someip.on_event(service_event, test)

    someip.register()
    someip.start()

    while True:
        time.sleep(3)
        if index == 0:  # let one send and rest get events
            someip.request(service_method, data=bytearray([65, 66, 67]))  # ABC


if __name__ == '__main__':
    Thread(target=service_example, args=()).start()
    time.sleep(5)
    for index in range(0, 3):
        Thread(target=client_example, args=(index,)).start()
        time.sleep(1)
    input()
