#!/usr/bin/env python
"""Server that accepts and executes control-type commands on the bot."""

import sys
import os
from inspect import getmembers, ismethod
from simplejson.decoder import JSONDecodeError
import zmq
import signal

# This is required to make imports work
sys.path = [os.getcwd()] + sys.path

import bot.lib.lib as lib
from bot.follower.follower import Follower
import pub_server as pub_server_mod
import bot.lib.messages as msgs

import bot.activity_solver.rubiks_solver as rubiks_mod
import bot.hardware.color_sensor as color_sensor_mod


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

    """Exports bot control via ZMQ.

    Most functionally exported by CtrlServer is in the form of methods
    exposed by the API. @lib.api_call decorators can be added to bot
    systems, which tags them for export. They can then be called
    remotely via CtrlClient, which is typically owned by an interface
    like the CLI, which typically accepts commands from an agent like
    a human.

    Some control is exported directly by CtrlServer, not through the
    API. For example, CtrlServer responds directly to ping messages,
    list messages (which give the objects/methods exposed by the API),
    and exit messages.

    CtrlServer is the primary owner of bot resources, which we call
    systems. For example, it's CtrlServer that instantiates gunner
    and follower. Through those two, CtrlServer owns the gun, the
    IR hub, the turret and basically every other bot system.

    The messages that CtrlServer accepts and responds with are fully
    specified in lib.messages. Make any changes to messages there.

    CtrlServer can be instructed (via the API) to spawn a new thread
    for a PubServer. When that happens, CtrlServer passes its systems
    to PubServer, which can read their state and publish it over a
    ZMQ PUB socket.

    """

    def __init__(self, testing=None, config_file="bot/config.yaml"):
        """Build ZMQ REP socket and instantiate bot systems.

        :param testing: True if running on simulated HW, False if on bot.
        :type testing: boolean
        :param config_file: Name of file to read configuration from.
        :type config_file: string

        """
        # Register signal handler, shut down cleanly (think motors)
        signal.signal(signal.SIGINT, self.signal_handler)

        # Load configuration and logger
        self.config = lib.get_config(config_file)
        self.logger = lib.get_logger()

        # Testing flag will cause objects to run on simulated hardware
        if testing is True or testing == "True":
            self.logger.info("CtrlServer running in test mode")
            lib.set_testing(True)
        elif testing is None:
            self.logger.info(
                "Defaulting to config testing flag: {}".format(
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
        except zmq.ZMQError:
            self.logger.error("ZMQ error. Is a server already running?")
            self.logger.warning("May be connected to an old server instance.")
            sys.exit(1)

        self.systems = self.assign_subsystems()
        self.logger.info("Control server initialized")

        # Don't spawn pub_server until told to
        self.pub_server = None

    def signal_handler(self, signal, frame):
        self.logger.info("Caught SIGINT (Ctrl+C), closing cleanly")
        self.clean_up()
        self.logger.info("Cleaned up bot, exiting...")
        sys.exit(0)

    def assign_subsystems(self):
        """Instantiates and stores references to bot subsystems.

        :returns: Dict of subsystems, maps system name to instantiated object.

        """

        self.follower = Follower()
        self.rubiks_solver = rubiks_mod.RubiksSolver()
        self.color_sensor = color_sensor_mod.ColorSensor()

        systems = {}
        systems["ctrl"] = self
        systems["follower"] = self.follower
        systems["driver"] = self.follower.driver
        systems["ir_hub"] = self.follower.ir_hub
        systems["rubiks"] = self.rubiks_solver
        systems["color"] = self.color_sensor

        self.logger.debug("Systems: {}".format(systems))
        return systems

    def listen(self):
        """Perpetually listen for messages, pass them to generic handler."""
        self.logger.info("Control server: {}".format(self.server_bind_addr))
        while True:
            try:
                msg = self.ctrl_sock.recv_json()
                reply = self.handle_msg(msg)
                self.logger.debug("Sending: {}".format(reply))
                self.ctrl_sock.send_json(reply)
            except JSONDecodeError:
                err_msg = "Not a JSON message!"
                self.logger.warning(err_msg)
                self.ctrl_sock.send_json(msgs.error(err_msg))
            except KeyboardInterrupt:
                self.logger.info("Exiting control server. Bye!")
                self.clean_up()
                sys.exit(0)

    def handle_msg(self, msg):
        """Generic message handler. Hands-off based on type of message.

        :param msg: Message, received via ZMQ from client, to handle.
        :type msg: dict
        :returns: An appropriate message reply dict, from lib.messages.

        """
        self.logger.debug("Received: {}".format(msg))

        try:
            msg_type = msg["type"]
        except KeyError as e:
            return msgs.error(e)

        if msg_type == "ping_req":
            reply = msgs.ping_reply()
        elif msg_type == "list_req":
            reply = self.list_callables()
        elif msg_type == "call_req":
            try:
                obj_name = msg["obj_name"]
                method = msg["method"]
                params = msg["params"]
                reply = self.call_method(obj_name, method, params)
            except KeyError as e:
                return msgs.error(e)
        elif msg_type == "exit_req":
            self.logger.info("Received message to die. Bye!")
            reply = msgs.exit_reply()
            # Need to actually send reply here as we're about to exit
            self.logger.debug("Sending: {}".format(reply))
            self.ctrl_sock.send_json(reply)
            self.clean_up()
            sys.exit(0)
        else:
            err_msg = "Unrecognized message: {}".format(msg)
            self.logger.warning(err_msg)
            reply = msgs.error(err_msg)
        return reply

    def list_callables(self):
        """Build list of callable methods on each exported subsystem object.

        Uses introspection to create a list of callable methods for each
        registered subsystem object. Only methods which are flagged using the
        @lib.api_call decorator will be included.

        :returns: list_reply message with callable objects and their methods.

        """
        self.logger.debug("List of callable API objects requested")
        # Dict of subsystem object names to their callable methods.
        callables = {}
        for name, obj in self.systems.items():
            methods = []
            # Filter out methods which are not explicitly flagged for export
            for member in getmembers(obj):
                if is_api_method(obj, member[0]):
                    methods.append(member[0])
            callables[name] = methods
        return msgs.list_reply(callables)

    def call_method(self, name, method, params):
        """Call a previously registered subsystem method by name. Only
        methods tagged with the @api_call decorator can be called.

        :param name: Assigned name of the registered subsystem.
        :type name: string
        :param method: Subsystem method to be called.
        :type method: string
        :param params: Additional parameters for the called method.
        :type params: dict
        :returns: call_reply or error message dict to be sent to caller.

        """
        self.logger.debug("API call: {}.{}({})".format(name, method, params))
        if name in self.systems:
            obj = self.systems[name]
            if is_api_method(obj, method):
                try:
                    # Calls given obj.method, unpacking and passing params dict
                    call_return = getattr(obj, method)(**params)
                    msg = "Called {}.{}".format(name, method)
                    self.logger.debug(msg + ",returned:{}".format(call_return))
                    return msgs.call_reply(msg, call_return)
                except TypeError:
                    # Raised when we have a mismatch of the method's kwargs
                    # TODO: Return argspec here?
                    err_msg = "Invalid params for {}.{}".format(name, method)
                    self.logger.warning(err_msg)
                    return msgs.error(err_msg)
                except Exception as e:
                    # Catch exception raised by called method, notify client
                    err_msg = "Exception: '{}'".format(str(e))
                    self.logger.warning(err_msg)
                    return msgs.error(err_msg)
            else:
                err_msg = "Invalid method: '{}.{}'".format(name, method)
                self.logger.warning(err_msg)
                return msgs.error(err_msg)
        else:
            err_msg = "Invalid object: '{}'".format(name)
            self.logger.warning(err_msg)
            return msgs.error(err_msg)

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
    def spawn_pub_server(self):
        """Spawn publisher thread."""
        if self.pub_server is None:
            self.pub_server = pub_server_mod.PubServer(self.systems)
            # Prevent pub_server thread from blocking the process from closing
            self.pub_server.setDaemon(True)
            self.pub_server.start()
            msg = "Spawned pub server"
            self.logger.info(msg)
            return msg
        else:
            err_msg = "PubServer is already running"
            self.logger.warning(err_msg)
            return err_msg

    @lib.api_call
    def stop_full(self):
        """Stop all drive and gun motors, set turret to safe state."""
        self.systems["driver"].move(0, 0)

    def clean_up(self):
        """Tear down ZMQ socket."""
        self.stop_full()
        self.ctrl_sock.close()
        self.context.term()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        server = CtrlServer(sys.argv[1])
    else:
        server = CtrlServer()
    server.listen()
