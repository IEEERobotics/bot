#!/usr/bin/env python

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

def is_api_method(obj, name):
    """Tests whether named method exists in obj and is flagged for API export""" 
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
    and exports selected functionality via JSON over ZeroMQ."""

    def __init__(self, testing=None, config_file="config.yaml"):

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

    def assign_subsystems(self):
        """Instantiates and stores referencs to bot specific bot subsytems

        :returns: A dictionary of subsystems, mapping a system name to an
        intantiated object

        """

        self.gunner = WheelGunner()
        self.follower = Follower()
        self.driver = self.follower.driver

        systems = {}
        systems["api"] = self
        systems["gunner"] = self.gunner
        systems["follower"] = self.follower
        systems["driver"] = self.follower.driver
        systems["turret"] = self.gunner.turret
        systems["gun"] = self.gunner.gun
        systems["ir_hub"] = self.follower.ir_hub
        return systems

    def register(self, name, obj):
        self.systems[name] = obj

    def listen(self):
        """Perpetually listen for new connections and hand off well-formed
        messages to a generic handler.  
        
        """

        self.logger.info("API server listening on {}".format(
                                                self.server_bind_addr))
        while True:
            try:
                msg = self.socket.recv_json()
                reply = self.handle_message(**msg)
                self.logger.debug("Sending API response: {}".format(reply))
                self.socket.send_json(reply)
            except JSONDecodeError:
                print "Not a JSON message!"
                self.socket.send_json(api_error('Not a JSON message!'))
            except KeyboardInterrupt:
                print "Bye!"
                sys.exit(0)

    def handle_message(self, cmd = None, opts = {}, **extra ):
        """Generic message handler.  Parse primary command and call the
        corresponding action.

        :param cmd: Command decoded directly from the JSON-dictioary received
        on the ZMQ request socket. 
        :type cmd: string
        :param opts: Options to pass on to the next level handler
        :type opts: dict
        :param extra: Additional (ignored) kwargs from dictionary expansion

        :returns: A standard API respoense dict.

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
            response = api_error('Unrecognized command')
        return response

    def list_callables(self):
        """Use introspection to create a list of callable methods for each 
        registered subsystem object.  Only methods which are flagged using the
        @lib.api_call decorator will be included.  

        :returns: A standard API response dict with a dict of callable objects
        as the result.

        """

        self.logger.info("List of API objects requested")
        response = {}
        for name,obj in self.systems.items():
            methods = []
            # filter out methods which are not explictily flagged for export
            for member in getmembers(obj):
                if is_api_method(obj, member[0]):
                    methods.append(member[0])
            response[name] = methods
        return api_success(msg='',result=response)

    def call_func(self, name = None, func = '', params = {}, **extra):
        """Call a previously registered subsystem function by name.  Only
        methods tagged with the @api_call decorator can be called.

        :param name: assigned name of the registered subsystem
        :type name: string
        :param func: subsystem method to be called
        :type func: string
        :param params: Additional parameters for the called function
        :type params: dict

        """

        self.logger.info("API call to: {}.{}({})".format(name,func,params))
        if name in self.systems:
            obj = self.systems[name]
            if is_api_method(obj, func):
                try:
                    result = getattr(obj, func)(**params)
                    return api_success('Called {}.{}'.format(name,func), result)
                except TypeError:
                    # This exception is raised when we have a mismatch of the
                    # method's kwargs
                    # TODO: return argspec here?
                    return api_error('Invalid params for {}.{}'.format(name,func))
                except Exception as e:
                    # We need to catch any exception raised by the called
                    # method and notify the client
                    return api_error("Exception: '{}'".format(str(e)))
            else:
                self.logger.debug("Invalid method")
                return api_error("Invalid method '{}.{}'".format(name,func))
        else:
            self.logger.debug("Invalid object")
            return api_error("Invalid object '{}'".format(name))

    @lib.api_call
    def echo(self, message = None):
        """Echo a message back to the caller """
        return message

    @lib.api_call
    def exception(self):
        """Raise a test exception which will be returned to the caller """
        raise Exception("Exception test")

if __name__ == '__main__':
    server = ApiServer(testing=True)
    server.listen()
  
