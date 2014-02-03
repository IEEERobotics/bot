# TODO(dfarrell07): Module-level docstring

from time import time
import zmq
from simplejson.decoder import JSONDecodeError

import client
from lib.messages import *

def api_method(ctrl_sock, obj_name, method):
    """Factory for ZMQ-based remote function calls.

    API methods map 1-1 with exported methods on the bot. When they are
    called, they pass that call on to the method they represent on the bot
    via ZMQ. They back up to a ZMQ message with the cmd key set to 'call'.

    :param ctrl_sock: ZMQ socket to control server, used when this method is called.
    :type ctrl_sock: zmq.core.socket.Socket
    :param obj_name: Name of the remote object that contains the method.
    :type obj_name: string
    :param method: Name of the remote method to call.
    :type method: string
    :returns: A function that calls the specified method via the ZMQ API.

    """
    def func(**kwargs):
        """Generated function that backs up to a ZMQ call to control server.

        :returns: Dict result returned by server.

        """
        opts = {"name": obj_name,"func": method, "params": kwargs}
        ctrl_sock.send_json(ctrl_cmd("call", opts))
        return ctrl_sock.recv_json()

    return func


class ApiClass(object):

    """Interface to a specific remote server object via the API.
    
    This class' methods are created during initialization according 
    to the initialization parameters.

    Note that 'interface' in this context has nothing to do with
    interfaces like the CLI (cli.py).

    """

    def __init__(self, ctrl_sock, obj_name, methods):
        """Build ZMQ-backed API call methods for this object.

        :param ctrl_sock: ZMQ REQ/REP socket to the on-bot CtrlServer.
        :type ctrl_sock: zmq.sugar.socket.Socket
        :param obj_name: Name of exported object that owns the given methods.
        :type obj_name: string
        :param methods: Exported methods owned by the given object.
        :type methods: string

        """
        self.name = obj_name
        self.api_methods = methods
        for method in methods:
            setattr(self, method, api_method(ctrl_sock, obj_name, method))


class CtrlClient(client.Client):

    """Used to issue control commands to the robot remotely.

    The control client should manage all command-type messages sent to the bot
    by interfaces. For exaple, if a user using the CLI (cli.py) wants to
    give a move command, the CtrlClient should be the object that actually
    sends that message over the wire.

    Clients, like the CtrlClient and PubClient, are typically owned by
    interfaces ('interface' is meant to imply the 'I' in CLI or GUI, not the
    programing concept, like Java-style interfaces). The interface accepts
    commands from the user and dispatches them to the appropriate client for
    interactions with the servers (like CtrlServer and PubServer).

    """

    def __init__(self, ctrl_addr="tcp://127.0.0.1:60000"):
        """Build ZMQ socket, connect to control server, discover exported objects.

        :param ctrl_addr: Address of control server to connect to via ZMQ.
        :type ctrl_addr: string

        """
        # Call superclass
        super(CtrlClient, self).__init__()

        # Build ZMQ socket to talk with control server
        self.ctrl_addr = ctrl_addr
        self.ctrl_sock = self.context.socket(zmq.REQ)
        self.ctrl_sock.connect(ctrl_addr)
        print "CtrlClient connected to CtrlServer at {}".format(ctrl_addr)
        self.discover()

    def recv(self):
        """Listen for JSON msg from server.

        :returns: Msg dict from server or empty dict if msg was invalid JSON.

        """
        try:
            result = self.ctrl_sock.recv_json()
        except JSONDecodeError:
            print "Non-JSON response from server"
            result = {}
        return result

    def discover(self):
        """Discover the remote objects exported by the control server and build a
        set of corresponding local objects that interface them. 

        TODO(dfarrell07): Shorten summary, add longer note here if needed.

        """
        # Send list command to server and get response
        self.ctrl_sock.send_json(ctrl_cmd("list"))
        reply = self.ctrl_sock.recv_json()

        # objects is a dict indexed by object name, whose values are lists of
        # method names
        self.objects = reply.get("result", {})
        for obj_name, methods in self.objects.items():
            setattr(self, obj_name, ApiClass(self.ctrl_sock, obj_name, methods))

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
        :returns: Result dict returned by remote control server.

        """
        opts = {"name": obj, "func": func, "params": params}
        self.ctrl_sock.send_json(ctrl_cmd("call", opts))
        return self.ctrl_sock.recv_json()

    def ping(self):
        """Ping the control server.

        :returns: Reply messages and reply time in seconds.

        """
        start = time()
        self.ctrl_sock.send_json(ctrl_cmd("ping"))
        reply = self.ctrl_sock.recv_json()
        reply_time = time() - start
        return reply, reply_time

    def clean_up(self):
        """Tear down ZMQ socket."""
        self.ctrl_sock.close()
        self.context.term()
