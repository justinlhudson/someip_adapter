import os, sys
import json
import threading
import time
import importlib
import tempfile
from enum import Enum
from typing import Callable, List, Tuple
import re
import socket


is_windows = sys.platform.startswith('win')


class SOMEIP:
    """
    Bindings for simple operations for service/client with
    vsomeip (<a href=https://github.com/COVESA/vsomeip>vsomip</a>)
    """
    class Message_Type(Enum):
        REQUEST = 0x00  # support
        REQUEST_NO_RETURN = 0x01
        NOTIFICATION = 0x02  # support
        REQUEST_ACK = 0x40
        REQUEST_NO_RETURN_ACK = 0x41
        NOTIFICATION_ACK = 0x42
        RESPONSE = 0x80  # support
        ERROR = 0x81
        RESPONSE_ACK = 0xC0
        ERROR_ACK = 0xC1
        UNKNOWN = 0xFF

    _configuration = {}  # global shared so routing service knows all the routes
    _lock = threading.Lock()
    _routing = None

    @staticmethod
    def _purge(pattern):
        dir = os.path.join(tempfile.gettempdir())
        retry = 3
        for f in os.listdir(dir):
            if re.search(pattern, f):
                while True:
                    retry = retry - 1
                    try:
                        os.remove(os.path.join(dir, f))
                    except Exception as ex:
                        time.sleep(1)
                        pass  # eat-it, Todo: not eat
                    if retry <0:
                        break

    def __init__(self, name: str, id: int, instance: int, configuration: dict={}, version: Tuple[int, int] = (0x00, 0x00), force=True):
        """
        create instance
        :param name: application name
        :param id: service id
        :param instance: service instance
        :param configuration: json style dictionary of vsomeip configuration file.
        :param version:
        :param force: remove any OS locks
        """
        self.module = importlib.import_module('vsomeip_ext')
        with SOMEIP._lock:  # protect while accessing external features
            self._name = name
            self._id = id
            self._instance = instance
            self._group = 0x00  # default (ALL), todo: support groups?
            self._is_service = None
            if configuration:
                SOMEIP._configuration = configuration
            else:
                SOMEIP._configuration = self.default()
            self._is_ready = False
            self._version = version

            if force:
                # https://github.com/COVESA/vsomeip/issues/289
                self._purge("vsomeip*.lck")

            if not SOMEIP._routing:
                SOMEIP._routing = self._name
            SOMEIP._configuration['routing'] = SOMEIP._routing

            # note: default configuration file if none given!!!
            with open('vsomeip.json', "w", newline='\n') as file_handle:
                json.dump(SOMEIP._configuration, file_handle, sort_keys=True, indent=2)
                file_handle.flush()

            self.module.create(self._name, self._id, self._instance)

    def __del__(self):
        """ cleanup """
        try:
            pass
        except OSError:
            pass  # eat-it, catch exception if not found

    @staticmethod
    def default():
        """
        default configuration template
        :return: configuration
        """
        configuration = {}
        with open(os.path.join(os.path.realpath(os.path.dirname(__file__)), 'templates', 'vsomeip_template.json'), "r") as handle:
            configuration = json.load(handle)

        configuration["unicast"] = '127.0.0.1'
        if is_windows:
            configuration["unicast"] = socket.gethostbyname(socket.gethostname())
        return configuration

    def configuration(self) -> dict:
        """
        reference of configuration used
        :return: configuration
        """
        if not SOMEIP._configuration:
            SOMEIP._configuration = self.default()
        return SOMEIP._configuration

    def start(self):
        """
        start application
        """
        self.module.start(self._name, self._id, self._instance)
        self._is_ready = True

    def stop(self):
        """
        stop application
        """
        with SOMEIP._lock:
            if SOMEIP._routing == self._name:  # if we are the router remove
                SOMEIP._routing = None

        self.module.stop(self._name, self._id, self._instance)
        self._is_ready = False

    def register(self):
        """
        register to service offering
        :except: 'UserWarning'
        """
        if self._is_service:
            raise UserWarning("client registers, service offer")
        self.module.request_service(self._name, self._id, self._instance, self._version[0], self._version[1])

    def request(self, id: int, data: bytearray = None, is_tcp: bool = False):
        """
        request message
        :param id: message id
        :param data: message data
        :param is_tcp: else udp  # todo: determine from configuration (e.g. "reliable")
        :except: 'UserWarning'
        """
        if self._is_service:
            raise UserWarning("client requests, service responds")

        if data is None:
            data = [0x00]  # NULL
        self.module.send_service(self._name, self._id, self._instance, id, -1 if is_tcp else 0, data)

    def callback(self, type: int, id: int, data: bytearray) -> bytearray:
        """
        :param id: message id
        :param data: message data
        :param type: enum Message_Type
        :return: message data
        """
        print(f"{type} -> id: {id}, data: {data}")

        # todo:  handle action based on request message type
        if self._is_service:  # only service responds to request if it has data in this case
            return data  # this is the response
        return None

    def on_message(self, id: int, callback: Callable[[int, int, bytearray], bytearray] = None):
        """
        register for message
        :param id: message id
        :param callback: function for on message
        """
        if callback is None:
            callback = self.callback
        self.module.register_message(self._name, self._id, self._instance, id, callback)

    def on_event(self, id: int, callback: Callable[[int, int, bytearray], bytearray] = None):
        """
        register for event
        :param id: event id (ex: 0x08??)
        :param callback: function for on event
        """
        if callback is None:
            callback = self.callback

        self.module.request_event_service(self._name, self._id, self._instance, id, self._group, self._version[0], self._version[1])
        self.on_message(id, callback)

    def offer(self, events: List[int] = None):
        """
        service and event offerings
        :param events: if any events to offer
        """
        self._is_service = True  # if offering something, then must be a service

        if events:
            for event in events:
                self.module.offer_event_service(self._name, self._id, self._instance, event, self._group)
        else:
            self.module.offer_service(self._name, self._id, self._instance, self._version[0], self._version[1])

    def notify(self, id: int, data: bytearray = None):
        """
        service event firing
        :param id:
        :param data:
        :except: 'UserWarning'
        """
        if not self._is_service:
            raise UserWarning("client consumes event")

        if data is None:
            data = bytearray([0x00])  # NULL, have to send something
        self.module.notify_clients(self._name, self._id, self._instance, id, data)
