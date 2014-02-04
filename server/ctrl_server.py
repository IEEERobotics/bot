#!/usr/bin/env python
"""Server that accepts and executes control-type commands on the bot."""

import sys
import os
from inspect import getmembers, ismethod
from simplejson.decoder import JSONDecodeError
import zmq

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
from gunner.wheel_gunner import WheelGunner
from follower.follower import Follower
import pub_server as pub_server_mod
from lib.messages import *


def is_api_method(obj, name):
    """Tests whether named method exists in obj and is flagged for API export.

    :param obj: API-exported object to search for the given method on.
    :type ojb: string
    :param name: Name of method to check for.
    :type name: string
    :returns: True if given method is on given obj and is exported, else False.

    """
    try:
        method = getattr(obj, name)
    except AttributeError:
        return False
    return (ismethod(method) and hasattr(method, "__api_call"))


class CtrlServer(object):

    """Network server that introspects the bot's registered subsystem objects
    and exports selected functionality via JSON over ZeroMQ.

    TODO(dfarrell07): Shorten summary, add longer note here if needed.

    """

    def __init__(self, testing=None, config_file="config.yaml"):
        # TODO(dfarrell07): Needs docstring

        # Load configuration and logger
        self.config = lib.get_config(config_file)
        self.logger = lib.get_logger()

        # Testing flag will cause objects to run on simulated hardware
        if testing:
            self.logger.info("CtrlServer running in test mode")
            lib.set_testing(True)
        elif testing is None:
            self.logger.info("Defaulting to config testing flag: {}".format(
                                                    self.config["testing"]))
            lib.set_testing(self.config["testing"])
        else:
            self.logger.info("CtrlServer running in non-test mode")
            lib.set_testing(False)

        # Build socket to listen for requests
        self.context = zmq.Context()
        self.ctrl_sock = self.context.socket(zmq.REP)
        self.server_bind_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["ctrl_server_port"])
        try:
            self.ctrl_sock.bind(self.server_bind_addr)
        except zmq.error.ZMQError:
            self.logger.error("ZMQ error. Is a server already running?")
            self.logger.warning("May be connected to an old server instance.")
            sys.exit(1)

        self.systems = self.assign_subsystems()
        self.logger.info("Control server initialized")

        # Don't spawn pub_server until told to
        self.pub_server = None

    def assign_subsystems(self):
        """Instantiates and stores references to bot specific bot subsystems.

        :returns: Dict of subsystems, maps system name to instantiated object.

        """

        self.gunner = WheelGunner()
        self.follower = Follower()

        systems = {}
        systems["ctrl"] = self
        systems["gunner"] = self.gunner
        systems["follower"] = self.follower
        systems["driver"] = self.follower.driver
        systems["turret"] = self.gunner.turret
        systems["gun"] = self.gunner.gun
        systems["ir_hub"] = self.follower.ir_hub
        self.logger.debug("Systems: {}".format(systems))
        return systems

    def listen(self):
        """Perpetually listen for new connections and hand off well-formed
        messages to a generic handler.

        TODO(dfarrell07): Shorten summary, add longer note here if needed.

        """
        self.logger.info("Control server listening on {}".format(
                                                self.server_bind_addr))
        while True:
            try:
                msg = self.ctrl_sock.recv_json()
                reply = self.handle_msg(msg)
                self.logger.debug("Sending: {}".format(reply))
                self.ctrl_sock.send_json(reply)
            except JSONDecodeError:
                err_msg = "Not a JSON message!"
                self.logger.warning(err_msg)
                self.ctrl_sock.send_json(ctrl_error(err_msg))
            except KeyboardInterrupt:
                self.logger.info("Exiting control server. Bye!")
                self.clean_up()
                sys.exit(0)

    def handle_msg(self, msg):
        """Generic message handler. Parse primary command and call the
        corresponding action.

        TODO(dfarrell07): Shorten summary and cmd description to one line.

        :param msg: Message, received via ZMQ from client, to handle.
        :type msg: dict
        :returns: A standard ctrl message response dict.

        """
        self.logger.debug("Received: {}".format(msg))

        try:
            if msg["type"] != "ctrl_cmd":
                return ctrl_error("CtrlServer expects ctrl_cmd messages")
            cmd = msg["cmd"]
            opts = msg["opts"]
        except KeyError as e:
            return ctrl_error(e)

        if cmd == "ping":
            response = ctrl_success("Ping reply")
        elif cmd == "list":
            response = self.list_callables()
        elif cmd == "call":
            response = self.call_func(**opts)
        else:
            err_msg = "Unrecognized command"
            self.logger.warning(err_msg)
            response = ctrl_error(err_msg)
        return response

    def list_callables(self):
        """Build list of callable methods on each exported subsystem object.

        Uses introspection to create a list of callable methods for each
        registered subsystem object. Only methods which are flagged using the
        @lib.api_call decorator will be included.

        :returns: ctrl_success msg with callable objects and their methods.

        """
        self.logger.debug("List of callable API objects requested")
        callables = {}
        for name, obj in self.systems.items():
            methods = []
            # Filter out methods which are not explicitly flagged for export
            for member in getmembers(obj):
                if is_api_method(obj, member[0]):
                    methods.append(member[0])
            callables[name] = methods
        msg = "Dict of subsystem object names to their callable methods."
        return ctrl_success(msg, result=callables)

    def call_func(self, name=None, func="", params={}, **extra):
        """Call a previously registered subsystem function by name. Only
        methods tagged with the @api_call decorator can be called.

        :param name: Assigned name of the registered subsystem.
        :type name: string
        :param func: Subsystem method to be called.
        :type func: string
        :param params: Additional parameters for the called function.
        :type params: dict
        :returns: Success/error message dict to be sent to caller.

        """
        self.logger.debug("API call to: {}.{}({})".format(name, func, params))
        if name in self.systems:
            obj = self.systems[name]
            if is_api_method(obj, func):
                try:
                    # Calls given obj.func, unpacking and passing params dict
                    call_result = getattr(obj, func)(**params)
                    msg = "Called {}.{}".format(name, func)
                    return ctrl_success(msg, call_result)
                except TypeError:
                    # This exception is raised when we have a mismatch of the
                    # method's kwargs
                    # TODO: return argspec here?
                    err_msg = "Invalid params for {}.{}".format(name, func)
                    self.logger.warning(err_msg)
                    return ctrl_error(err_msg)
                except Exception as e:
                    # We need to catch any exception raised by the called
                    # method and notify the client
                    err_msg = "Exception: '{}'".format(str(e))
                    self.logger.warning(err_msg)
                    return ctrl_error(err_msg)
            else:
                err_msg = "Invalid method: '{}.{}'".format(name, func)
                self.logger.warning(err_msg)
                return ctrl_error(err_msg)
        else:
            err_msg = "Invalid object: '{}'".format(name)
            self.logger.warning(err_msg)
            return ctrl_error(err_msg)

    @lib.api_call
    def echo(self, msg=None):
        """Echo a message back to the caller.

        :param msg: Message to be echoed back to caller, default is None.
        :returns: Message given by param, defaults to None.

        """
        return msg

    @lib.api_call
    def exception(self):
        """Raise a test exception which will be returned to the caller."""
        raise Exception("Exception test")

    @lib.api_call
    def kill_server(self):
        exit_msg = "Received message to die. Bye!"
        self.logger.info(exit_msg)
        reply = ctrl_success(exit_msg)
        # Need to actually send reply here as we're about to exit
        self.logger.debug("Sending: {}".format(reply))
        self.ctrl_sock.send_json(reply)
        self.clean_up()
        sys.exit(0)

    @lib.api_call
    def spawn_pub_server(self):
        """Spawn publisher thread."""
        if self.pub_server is None:
            self.pub_server = pub_server_mod.PubServer(self.systems)
            # Prevent pub_server thread from blocking the process from closing
            self.pub_server.setDaemon(True)
            self.pub_server.start()
            msg = "Spawned pub server"
            self.logger.info(msg)
            return ctrl_success(msg)
        else:
            err_msg = "Pub server is already running"
            self.logger.warning(err_msg)
            return ctrl_error(err_msg)

    def clean_up(self):
        """Tear down ZMQ socket."""
        self.ctrl_sock.close()
        self.context.term()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        server = CtrlServer(sys.argv[1])
    else:
        server = CtrlServer()
    server.listen()
