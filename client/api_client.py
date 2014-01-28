#!/usr/bin/env python
# TODO(dfarrell07): Module-level docstring

from time import time
import zmq
from simplejson.decoder import JSONDecodeError

from client import Client


def api_method(api_sock, obj_name, method):
    """Factory for ZMQ-based remote function calls.

    :param api_sock: ZMQ socket to API server, used when this method is called.
    :type api_sock: zmq.core.socket.Socket
    :param obj_name: Name of the remote object that contains the method.
    :type obj_name: string
    :param method: Name of the remote method to call.
    :type method: string
    :returns: A function that calls the specified method via the ZMQ API.

    """
    def func(**kwargs):
        """Generated function that backs up to a ZMQ call to API server.

        :returns: Dict result returned by server.

        """
        api_sock.send_json({'cmd': 'call', 'opts': {'name': obj_name,
                                    'func': method, 'params': kwargs}})
        result = api_sock.recv_json()
        return result

    return func


class ApiClass(object):

    """Interface to a specific remote server object via the API.
    
    This class' methods are created during initialization according 
    to the initialization parameters

    """

    def __init__(self, api_sock, obj_name, methods):
        # TODO(dfarrell07): Docstring
        # Build ZMQ-backed API call methods for this object
        self.name = obj_name
        self.api_methods = methods
        for method in methods:
            setattr(self, method, api_method(api_sock, obj_name, method))


class ApiClient(Client):

    # TODO(dfarrell07): Docstring

    def __init__(self, api_addr='tcp://127.0.0.1:60000'):
        """Build ZMQ socket, connect to API server, discover exported objects.

        :param api_addr: Address of API server to connect to via ZMQ.
        :type api_addr: string

        """
        # Build ZMQ socket to talk with API server
        self.api_addr = api_addr
        self.context = zmq.Context()
        self.api_sock = self.context.socket(zmq.REQ)
        self.api_sock.connect(api_addr)
        print "Connected to server at {}".format(api_addr)
        self.discover()

    # TODO: should init/teardown be wrapped in a python context manager?
    def cleanUp(self):
        """Tear down ZMQ socket."""
        self.api_sock.close()
        self.context.term()

    def recv(self):
        """Listen for JSON msg from server.

        :returns: Msg dict from server or empty dict if msg was invalid JSON.

        """
        try:
            result = self.api_sock.recv_json()
        except JSONDecodeError:
            print "Non-JSON response from server"
            result = {}
        return result

    def discover(self):
        """Discover the remote objects exported by the API server and build a
        set of corresponding local objects that interface them. 

        TODO(dfarrell07): Shorten summary, add longer note here if needed.

        """
        self.api_sock.send_json({'cmd': 'list'})
        reply = self.recv()
        self.objects = reply.get('result', {})
        # objects is a dict indexed by object name, whose values are lists of
        # method names
        for obj_name, methods in self.objects.items():
            setattr(self, obj_name, ApiClass(self.api_sock, obj_name, methods))

    def call(self, obj, func, params = {}):
        """Call a remote API method by name.  

        This is an alternate interface to the remote API, useful when
        calling the locally constructed methods would simply add an
        extra layer of name parsing.  Most useful for text-based clients.

        :param obj: Remote object on which to call a function over ZMQ.
        :type obj: string
        :param func: Remote function to call over ZMQ.
        :type func: string
        :param params: Params to pass to remote function, called over ZMQ.
        :type params: dict
        :returns: Result dict returned by remote API server.

        """
        opts = {}
        opts["name"] = obj
        opts["func"] = func
        opts["params"] = params
        return self.send_cmd("call", self.api_sock, opts)

    def ping(self):
        """Ping the remote API.

        :returns: Reply messages and reply time in seconds.

        """
        cmd = "ping"
        start = time()
        reply = self.send_cmd(cmd, self.api_sock)
        reply_time = time() - start
        return reply, reply_time
