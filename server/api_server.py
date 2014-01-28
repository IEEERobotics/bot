#!/usr/bin/env python
# TODO(dfarrell07): Needs module docstring

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


def is_api_method(obj, name):
    """Tests whether named method exists in obj and is flagged for API export.

    :param name: TODO
    :type name: TODO

    """ 
    try:
        method = getattr(obj, name)
    except AttributeError:
        return False
    return (ismethod(method) and hasattr(method, '__api_call'))


def api_success(msg = '', result = None):
    return { 'status':'success', 'msg':msg, 'result':result }


def api_error(msg = ''):
    return { 'status':'error', 'msg': msg }


class ApiServer(object):

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
            self.logger.info("Server running in test mode")
            lib.set_testing(True)
        elif testing is None:
            self.logger.info("Defaulting to config testing flag: {}".format(
                                                    self.config["testing"]))
            lib.set_testing(self.config["testing"])
        else:
            self.logger.info("Server running in non-test mode")
            lib.set_testing(False)

        # Build socket to listen for requests
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.server_bind_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["server_port"])
        self.socket.bind(self.server_bind_addr)

        self.systems = self.assign_subsystems()
        self.logger.info("API server initialized")

        # Don't spawn pub_server until told to via API
        self.pub_server = None

    def assign_subsystems(self):
        """Instantiates and stores references to bot specific bot subsystems.

        :returns: Dict of subsystems, maps system name to instantiated object.

        """

        self.gunner = WheelGunner()
        self.follower = Follower()

        systems = {}
        systems["api"] = self
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
        self.logger.info("API server listening on {}".format(
                                                self.server_bind_addr))
        while True:
            try:
                msg = self.socket.recv_json()
                # TODO(dfarrell07): Document ** clearly
                reply = self.handle_message(**msg)
                self.logger.debug("Sending API response: {}".format(reply))
                self.socket.send_json(reply)
            except JSONDecodeError:
                self.logger.warning("Not a JSON message!")
                self.socket.send_json(api_error('Not a JSON message!'))
            except KeyboardInterrupt:
                self.logger.info("Exiting API server. Bye!")
                sys.exit(0)

    def handle_message(self, cmd=None, opts={}, **extra):
        """Generic message handler.  Parse primary command and call the
        corresponding action.

        TODO(dfarrell07): Shorten summary and cmd description to one line.

        :param cmd: Command decoded directly from the JSON-dictionary received
        on the ZMQ request socket. 
        :type cmd: string
        :param opts: Options to pass on to the next level handler
        :type opts: dict
        :param extra: Additional (ignored) kwargs from dictionary expansion
        :returns: A standard API response dict.

        """
        self.logger.debug("API server received cmd: {}, opts: {}".format(
                                                                cmd, opts))
        if cmd == 'ping':
            response = api_success()
        elif cmd == 'list':
            response = self.list_callables()
        elif cmd == 'call':
            response = self.call_func(**opts)
        else:
            self.logger.warning("Unrecognized command")
            response = api_error('Unrecognized command')
        return response

    def list_callables(self):
        """Use introspection to create a list of callable methods for each 
        registered subsystem object.  Only methods which are flagged using the
        @lib.api_call decorator will be included.  

        :returns: A standard API response dict with a dict of callable objects
        as the result.

        TODO(dfarrell07): Shorten summary and returns to one line.
        TODO(dfarrell07): Any reason this shouldn't be accessible from call?

        """
        self.logger.debug("List of API objects requested")
        response = {}
        for name,obj in self.systems.items():
            methods = []
            # Filter out methods which are not explicitly flagged for export
            for member in getmembers(obj):
                if is_api_method(obj, member[0]):
                    methods.append(member[0])
            response[name] = methods
        return api_success(msg='', result=response)

    def call_func(self, name=None, func='', params={}, **extra):
        """Call a previously registered subsystem function by name.  Only
        methods tagged with the @api_call decorator can be called.

        :param name: Assigned name of the registered subsystem.
        :type name: string
        :param func: Subsystem method to be called.
        :type func: string
        :param params: Additional parameters for the called function.
        :type params: dict

        """
        self.logger.debug("API call to: {}.{}({})".format(name,func,params))
        if name in self.systems:
            obj = self.systems[name]
            if is_api_method(obj, func):
                try:
                    # TODO(dfarrell07): Document this call more clearly
                    result = getattr(obj, func)(**params)
                    return api_success('Called {}.{}'.format(name,func), result)
                except TypeError:
                    # This exception is raised when we have a mismatch of the
                    # method's kwargs
                    # TODO: return argspec here?
                    err_msg = 'Invalid params for {}.{}'.format(name,func)
                    self.logger.warning(err_msg)
                    return api_error(err_msg)
                except Exception as e:
                    # We need to catch any exception raised by the called
                    # method and notify the client
                    err_msg = "Exception: '{}'".format(str(e))
                    self.logger.warning(err_msg)
                    return api_error(err_msg)
            else:
                err_msg = "Invalid method '{}.{}'".format(name,func)
                self.logger.warning(err_msg)
                return api_error(err_msg)
        else:
            err_msg = "Invalid object '{}'".format(name)
            self.logger.warning(err_msg)
            return api_error(err_msg)

    @lib.api_call
    def echo(self, message=None):
        """Echo a message back to the caller.

        :param message: Message to be echoed back to caller, default is None.
        :returns: Message given by param, defaults to None.

        """
        return message

    @lib.api_call
    def exception(self):
        """Raise a test exception which will be returned to the caller."""
        raise Exception("Exception test")

    @lib.api_call
    def kill_server(self):
        self.logger.info("Received message to die. Bye!")
        reply = api_success("Received message to die. Bye!")
        # Need to actually send reply here as we're about to exit
        self.logger.debug("Sending API response: {}".format(reply))
        self.socket.send_json(reply)
        # TODO(dfarrell07): Better cleanup?
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
            return api_success(msg)
        else:
            err_msg = "Pub server is already running"
            self.logger.warning(err_msg)
            return api_error(err_msg)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        server = ApiServer(sys.argv[1])
    else:
        server = ApiServer()
    server.listen()
