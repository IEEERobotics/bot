#!/usr/bin/env python

import time
import zmq
from simplejson.decoder import JSONDecodeError

def api_method(socket, obj_name, method):
    """Factory for ZMQ-based remote function calls.

    :param socket: An initialized API client socket to use when this method is
    called
    :param obj_name: Name of the remote object that contains the method
    :param method: Name of the remote method to call
    :returns: A function that calls the specified method via the ZMQ API

    """
    def func(** kwargs):
        socket.send_json({'cmd':'call', 'opts': { 'name':obj_name, 
                                    'func':method, 'params':kwargs } } )
        result = socket.recv_json()
        return result

    return func

class ApiClass(object):
    """Interface to a specific remote server object via the API.
    
    This class' methods are created during initialization according 
    to the initialization parameters

    """
    def __init__(self, socket, obj_name, methods):
        # Build ZMQ-backed API call methods for this object
        self.name = obj_name
        self.api_methods = methods
        for method in methods:
            setattr(self, method, api_method(socket, obj_name, method))

class ApiClient(object):

    def __init__(self, address = 'tcp://127.0.0.1:60000'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self.discover()

    # TODO: should init/teardown be wrapped in a python context manager?
    def cleanUp(self):
        """Tear down ZMQ socket."""
        self.socket.close()
        self.context.term()

    def recv(self):
        """Receive a JSON-encoded message from the server, attempt to decode
        and handle exceptions resulting from invalid messages.

        """
        try:
            result = self.socket.recv_json()
        except JSONDecodeError:
            print "Non-JSON response from server"
            result = {}
        return result

    def discover(self):
        """Discover the remote objects exported by the API server and build a
        set of corresopnding local objects that interface them. 

        """
        self.socket.send_json({'cmd':'list'})
        reply = self.recv()
        self.objects = reply.get('result', {})
        # objects is a dict indexed by object name, whose values are lists of
        # method names
        for obj_name,methods in self.objects.items():
            setattr(self, obj_name, ApiClass(self.socket, obj_name, methods))

    def call(self, obj, func, params = {}):
        """Call a remote API method by name.  

        This is an alternate interface to the remote API, useful when
        calling the locally constructed methods would simply add an
        extra layer of name parsing.  Most useful for text-based clients.

        """
        self.socket.send_json({'cmd':'call', 'opts': {'name':obj, 'func':func, 'params':params}})
        result = self.socket.recv()
        return result

    def ping(self):
        """Ping the remote API.

        :returns: response time in seconds, standard API response dict

        """
        start = time.time()
        self.socket.send_json({'cmd':'ping'})
        reply = self.socket.recv()
        return time.time() - start, reply

