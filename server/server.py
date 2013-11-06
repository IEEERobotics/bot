#!/usr/bin/env python
"""Server for handling interaction between clients and bot."""

import sys
import os
from time import sleep
from math import fabs
import traceback

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

try:
    import yaml
except ImportError, err:
    sys.stderr.write("ERROR: {}. Try installing python-yaml.\n".format(err))
    raise

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import driver.mec_driver as md_mod
import hardware.wheel_gun as wgun_mod
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod


class Server(object):

    """Listen for client commands and make them happen on the bot."""

    def __init__(self, testing=None):
        """Build all main bot objects, set ZMQ to listen."""
        # Load configuration and logger
        self.config = lib.load_config()
        self.logger = lib.get_logger()

        # Testing flag will cause objects to run on simulated hardware
        if testing == "True":
            self.logger.info("Server will build bot objects in test mode")
            lib.set_testing(True)
        elif testing == "False":
            self.logger.info("Server will build bot objects in non-test mode")
            lib.set_testing(False)
        else:
            self.logger.info("Defaulting to config testing flag: {}".format(
                                                    self.config["testing"]))
            lib.set_testing(self.config["testing"])

        # Listen for incoming requests
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.server_bind_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["server_port"])
        self.socket.bind(self.server_bind_addr)

        # Build MecDriver, which will accept and handle movement actions
        self.driver = md_mod.MecDriver()

        # Build WheelGun (TODO: incorporate into gunner)
        self.gun = wgun_mod.WheelGun()

        # Build WheelGunner, which will accept and handle fire actions
        self.gunner = wg_mod.WheelGunner()

        # Build follower, which will manage following line
        self.follower = f_mod.Follower()

    def listen(self):
        """Listen for messages, pass them off to be handled and send reply."""
        self.logger.info("Server listening on {}".format(
                                                self.server_bind_addr))
        while True:
            # TODO: Use recv_json to avoid having to parse input separately?
            msg_raw = self.socket.recv()
            self.logger.debug("Received: {}".format(msg_raw))

            # TODO: Send JSON object directly using send_json?
            #       All handle_*() methods must then return a dict.
            reply_msg = self.handle_msg(msg_raw)
            self.logger.debug("Replying: {}".format(reply_msg))
            self.socket.send(reply_msg)

    def handle_msg(self, msg_raw):
        """Confirm message format and take appropriate action.

        :param msg_raw: Raw message string received by ZMQ.
        :type msg_raw: string
        :returns: Success or error message with description.

        """
        try:
            msg = dict(yaml.safe_load(msg_raw))
            cmd = msg["cmd"]
            assert type(cmd) is str
        except ValueError:
            return "Error: Unable to convert message to dict"
        except KeyError:
            return "Error: No 'cmd' key given"
        except AssertionError:
            return "Error: Key 'cmd' is not a string"
        except yaml.parser.ParserError:
            return "Error: Unable to parse msg as YAML: {}".format(msg_raw)

        try:
            # TODO: Not all handle_*()s require opts; standardize this?
            opts = msg["opts"]
            assert type(opts) is dict
        except KeyError:
            return "Error: No 'opts' key given"
        except AssertionError:
            return "Error: Key 'opts' is not a dict"

        # TODO: Switch from if..else to a string -> function map (dict)
        if cmd == "fwd_strafe_turn":
            return self.handle_fwd_strafe_turn(opts)
        elif cmd == "move":
            return self.handle_move(opts)
        elif cmd == "rotate":
            return self.handle_rotate(opts)
        elif cmd == "auto_fire":
            return self.handle_auto_fire()
        elif cmd == "aim":
            return self.handle_aim(opts)
        elif cmd == "advance_dart":
            return self.handle_advance_dart()
        elif cmd == "fire_speed":
            return self.handle_fire_speed(opts)
        elif cmd == "laser":
            return self.handle_laser(opts)
        elif cmd == "spin":
            return self.handle_spin(opts)
        elif cmd == "fire":
            return self.handle_fire()
        elif cmd == "die":
            self.handle_die()
        else:
            return "Error: Unknown cmd {}".format(cmd)

    def handle_fwd_strafe_turn(self, opts):
        """Validate options and make move call to driver.

        Speed should be between 0-100, angle between 0-360.

        :param opts: Dict with keys 'speed' and 'angle' to move.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate fwd option
        try:
            fwd = float(opts["fwd"])
        except KeyError:
            return "Error: No 'fwd' opt given"
        except ValueError:
            return "Error: Could not convert fwd to float"

        # Validate strafe option
        try:
            strafe = float(opts["strafe"])
        except KeyError:
            return "Error: No 'strafe' opt given"
        except ValueError:
            return "Error: Could not convert strafe to float"

        # Validate turn option
        try:
            turn = float(opts["turn"])
        except KeyError:
            return "Error: No 'turn' opt given"
        except ValueError:
            return "Error: Could not convert turn to float"

        # Make call to driver
        try:
            # Rotate only when turn dominates
            if fabs(turn) > fabs(fwd) and fabs(turn) > fabs(strafe):
                self.driver.rotate(turn)
            else:
                self.driver.move_forward_strafe(fwd, strafe)
        except Exception:
            tb = traceback.format_exc()
            return "Error from driver: {}".format(tb)

        return "Success: {}".format(opts)

    def handle_move(self, opts):
        """Validate options and make move call to driver.

        Speed should be between 0-100, angle between 0-360.

        :param opts: Dict with keys 'speed' and 'angle' to move.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate speed option
        try:
            speed = float(opts["speed"])
        except KeyError:
            return "Error: No 'speed' opt given"
        except ValueError:
            return "Error: Could not convert speed to float"

        # Validate angle option
        try:
            angle = float(opts["angle"])
        except KeyError:
            return "Error: No 'angle' opt given"
        except ValueError:
            return "Error: Could not convert angle to float"

        # Make call to driver
        try:
            self.driver.move(speed=speed, angle=angle)
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: {}".format(opts)

    def handle_rotate(self, opts):
        """Validate options and make rotate call to driver.

        :param opts: Dict with key 'speed' to rotate, -100 to 100.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate speed option
        try:
            rotate_speed = float(opts["speed"])
        except KeyError:
            return "Error: No 'speed' opt given"
        except ValueError:
            return "Error: Could not convert speed to float"

        # Make call to driver
        try:
            self.driver.rotate(rotate_speed=rotate_speed)
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: {}".format(opts)

    def handle_auto_fire(self):
        """Make fire call to gunner. Normally used in autonomous mode.

        :returns: success or error message with description.

        """
        # Make call to gunner
        try:
            self.gunner.auto_fire()
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: Fired"

    def handle_aim(self, opts):
        """Validate options and make call to gunner.

        :param opts: Dict with keys 'x' and 'y' (angles 0-180).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate x angle option
        try:
            yaw = int(round(opts["yaw"]))
        except KeyError:
            return "Error: No 'yaw' opt given"
        except TypeError:
            return "Error: Could not convert yaw to int"

        # Validate y angle option
        try:
            pitch = int(round(opts["pitch"]))
        except KeyError:
            return "Error: No 'pitch' opt given"
        except TypeError:
            return "Error: Could not convert pitch to int"

        # Make call to gunner
        try:
            self.gunner.aim_turret(yaw, pitch)
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: {}".format(opts)

    def handle_advance_dart(self):
        """Make call to gunner to advance a dart.

        :returns: Success or error message with description.

        """
        try:
            self.gunner.advance_dart()
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: Advanced dart"

    def handle_fire_speed(self, opts):
        """Set rotation speed of firing wheels.

        :param opts: Dict with key 'speed' (0-100).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate speed option
        try:
            speed = int(round(opts["speed"]))
        except KeyError:
            return "Error: No 'speed' opt given"
        except TypeError:
            return "Error: Could not convert speed to int"

        # Make call to gunner
        try:
            self.gunner.wheel_speed = speed
        except Exception as e:
            return "Error: {}".format(e)

        return "Success: {}".format(opts)

    def handle_laser(self, opts):
        """Turn laser ON or OFF.

        :param opts: Dict with key 'state' (0/1).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate state option
        try:
            state = int(round(opts["state"]))
        except KeyError:
            return "Error: No 'state' opt given"
        except TypeError:
            return "Error: Could not convert state to int"

        # Make call to gun
        try:
            result = self.gun.laser(state)
            return "Success: {{result: {}}}".format(result)
            # TODO: Return JSON object / dict, with status, result [, msg]
        except Exception as e:
            return "Error: {}".format(e)

    def handle_spin(self, opts):
        """Turn gun motor spin ON or OFF.

        :param opts: Dict with key 'state' (0/1).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate state option
        try:
            state = int(round(opts["state"]))
        except KeyError:
            return "Error: No 'state' opt given"
        except TypeError:
            return "Error: Could not convert state to int"

        # Make call to gun
        try:
            result = self.gun.spin(state)
            return "Success: {{result: {}}}".format(result)
            # TODO: Return JSON object / dict, with status, result [, msg]
        except Exception as e:
            return "Error: {}".format(e)

    def handle_fire(self):
        """Make fire call to gun, using default parameters.

        :returns: Success or error message with description.

        """
        # Make call to gun
        try:
            result = self.gun.fire()
            return "Success: {{result: {}}}".format(result)
            # TODO: Return JSON object / dict, with status, result [, msg]
        except Exception as e:
            return "Error: {}".format(e)

    def handle_die(self):
        """Accept poison pill and gracefully exit.

        Note that this method needs to print and send the reply itself,
        as it exits the process before listen() could take those actions.

        """
        self.logger.info("Success: Received message to die. Bye!")
        self.socket.send("Success: Received message to die. Bye!")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        server = Server(sys.argv[1])
    else:
        server = Server()
    server.listen()
