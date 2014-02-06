"""Exposes bot systems and accepts/issues control-type commands."""

from time import time
import zmq
from simplejson.decoder import JSONDecodeError

import lib.messages as msgs


def api_method(ctrl_sock, obj_name, method):
    """Factory for ZMQ-based remote function calls.

    API methods map 1-1 with exported methods on the bot. When they are
    called, they pass that call on to the method they represent on the bot
    via ZMQ. They back up to a ZMQ message with the cmd key set to 'call'.

    :param ctrl_sock: ZMQ socket to CtrlServer, used when method is called.
    :type ctrl_sock: zmq.core.socket.Socket
    :param obj_name: Name of the remote object that contains the method.
    :type obj_name: string
    :param method: Name of the remote method to call.
    :type method: string
    :returns: A function that calls the specified method via the ZMQ API.

    """
    def func(**params):
        """Generated function that backs up to a ZMQ call to control server.

        :returns: Dict result returned by server.

        """
        ctrl_sock.send_json(msgs.call_req(obj_name, method, params))
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


class CtrlClient(object):

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
        """Build ZMQ socket, connect to CtrlServer, discover exported objects.

        :param ctrl_addr: Address of control server to connect to via ZMQ.
        :type ctrl_addr: string

        """
        # Build ZMQ socket to talk with control server
        self.context = zmq.Context()
        self.ctrl_addr = ctrl_addr
        self.ctrl_sock = self.context.socket(zmq.REQ)
        self.ctrl_sock.connect(ctrl_addr)
        self.discover()
        print "CtrlClient connected to CtrlServer at {}".format(ctrl_addr)

    def discover(self):
        """Gets list of exported objects/methods, maps to local attributes.

        Discover the remote objects exported by the control server and build a
        set of corresponding local objects that interface them.

        """
        # Send list command to server and get response
        self.ctrl_sock.send_json(msgs.list_req())
        reply = self.ctrl_sock.recv_json()

        if reply["type"] != "list_reply":
            print "Error discovering objects: {}".format(reply)
            return False

        # 'self.objects' is a dict indexed by object name, whose values
        # are lists of method names.
        self.objects = reply["objects"]

        # Creates/updates CtrlClient instance vars, giving them the
        # names of exported objects. Each stores an ApiClass that acts
        # as a local representation of that object (including its
        # exported methods).
        for obj_name, methods in self.objects.items():
            setattr(self, obj_name, ApiClass(self.ctrl_sock, obj_name, methods))

    def call(self, obj_name, method, params):
        """Call a remote API method by name.

        This is an alternate interface to the remote API, useful when
        calling the locally constructed methods would simply add an
        extra layer of name parsing. Most useful for text-based clients.

        :param obj_name: Remote object on which to call a method over ZMQ.
        :type obj_name: string
        :param method: Remote method to call over ZMQ.
        :type method: string
        :param params: Params to pass to remote method, called over ZMQ.
        :type params: dict
        :returns: Result dict returned by remote control server.

        """
        self.ctrl_sock.send_json(msgs.call_req(obj_name, method, params))
        return self.ctrl_sock.recv_json()

    def exit_server(self):
        """Send a message to the server, asking it to die.

        :returns: Reply message from the server.

        """
        self.ctrl_sock.send_json(msgs.exit_req())
        return self.ctrl_sock.recv_json()

    def ping(self):
        """Ping the control server.

        :returns: Reply time in milliseconds.

        """
        start = time()
        self.ctrl_sock.send_json(msgs.ping_req())
        reply = self.ctrl_sock.recv_json()
        reply_time = (time() - start) * 1000
        if reply["type"] != "ping_reply":
            print "Ping failed: {}".format(reply)
        return reply_time

    def clean_up(self):
        """Tear down ZMQ socket."""
        self.ctrl_sock.close()
        self.context.term()
