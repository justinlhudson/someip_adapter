import time
import uuid
from threading import Thread
from someip_adapter.vsomeip import SOMEIP

SERVICE_ID_DEFAULT = 0x1234
SERVICE_INSTANCE_DEFAULT = 0x5678
SERVICE_PORT_DEFAULT = 30509

def service_example(index: int = 0):
    configuration = SOMEIP.default()

    service_name = "service_example" + f"_{index}" + f"_{uuid.uuid4().hex.upper()[0:6]}"
    service_id = SERVICE_ID_DEFAULT + index
    service_instance = SERVICE_INSTANCE_DEFAULT
    service_port = SERVICE_PORT_DEFAULT + index

    configuration["applications"].append({'name': service_name, 'id': 0x1111 + index})
    configuration["services"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})

    service_events = [0x8770+index]
    service_method = 0x9002

    def test(type: int, id: int, data: bytearray) -> bytearray:
        print(f"rx: {hex(id)}, {type} ({service_name}, {service_port}), data: {data}")
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


def client_example(index: int = 0, increment: int = 0):
    configuration = SOMEIP.default()

    client_name = "client_example" + f"_{increment}" + f"_{index}" + f"_{uuid.uuid4().hex.upper()[0:6]}"
    service_id = SERVICE_ID_DEFAULT + increment
    service_instance = SERVICE_INSTANCE_DEFAULT
    service_port = SERVICE_PORT_DEFAULT + increment

    configuration["applications"].append({'name': client_name, 'id': 0x2222 + index})
    configuration["clients"].append({'service': service_id, 'instance': service_instance, 'unreliable': service_port})
    service_method = 0x9002
    service_events = [0x8770 + increment]  # 0x8XXX

    def test(type: int, id: int, data: bytearray) -> bytearray:
        print(f"rx: {hex(id)}, {type} ({client_name}, {service_port}), data: {data}")
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
    init = 0
    services = 3
    clients = 3
    
    for x in range(init, init + services):
        Thread(target=service_example, args=(x,)).start()
        time.sleep(5)
        for y in range(init, init + clients):
            Thread(target=client_example, args=(y, x)).start()
            time.sleep(3)
    input()
