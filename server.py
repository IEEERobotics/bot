#!/usr/bin/env python
"""Lightweight server to start/stop controllers."""

import sys
from time import sleep

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

import lib.lib as lib
import driver.mec_driver as md_mod
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod


class Server(object):

    """Start/stop controllers when instructed via server port."""

    def __init__(self, testing=False):
        """Build logger, set ZMQ to listen on server port."""
        # TODO(dfarrell07): Build server logger, don't reuse bot logger

        lib.set_testing(bool(testing))

        # Load and store configuration
        self.config = lib.load_config()

        # Listen for incoming requests
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.config["server_port"])
        #print "Server bound to {}".format(self.config["server_port"])

        # Build MecDriver, which will accept and handle movement actions
        self.driver = md_mod.MecDriver()

        # Build WheelGunner, which will accept and handle fire actions
        self.gunner = wg_mod.WheelGunner()

        # Build follower, which will manage following line
        self.follower = f_mod.Follower()

    def listen(self):
        """Listen for messages, pass them off to be handled and send reply."""
        while True:
            #print "Listening for message..."
            msg_raw = self.socket.recv()
            #print "Received: {}".format(msg_raw)

            reply_msg = self.handle_msg(msg_raw)
            #print "Replying: {}".format(reply_msg)
            self.socket.send(reply_msg)

    def handle_msg(self, msg_raw):
        """Confirm message format and take appropriate action.

        :param msg_raw: Raw message string received by ZMQ.
        :type msg_raw: string
        :returns: Success or failure message, plus description.

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

        try:
            opts = msg["opts"]
            assert type(opts) is dict
        except KeyError:
            return "Error: No 'opts' key given"
        except AssertionError:
            return "Error: Key 'opts' is not a dict"

        if cmd == "move":
            return self.handle_move(opts)
        elif cmd == "rotate":
            return self.handle_rotate(opts)
        elif cmd == "fire":
            return self.handle_fire(opts)
        elif cmd == "aim_turret":
            return self.handle_aim_turret(opts)
        elif cmd == "advance_dart":
            return self.handle_advance_dart()
        elif cmd == "fire_speed":
            return self.handle_fire_speed(opts)
        elif cmd == "die":
            self.handle_die()
        else:
            return "Error: Unknown cmd {}".format(cmd)

    def handle_move(self, opts):
        """Validate options and make move call to driver.

        Speed should be between 0-100, angle between 0-360.

        :param opts: Dict with keys 'speed' and 'angle' to move.
        :type opts: dict

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

    def handle_rotate(self, opts):
        """Validate options and make rotate call to driver.

        :param opts: Dict with key 'speed' to rotate, -100 to 100.
        :type opts: dict

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

    def handle_fire(self):
        """Make fire call to gunner."""
        # Make call to gunner
        try:
            self.gunner.fire()
        except Exception as e:
            return "Error: {}".format(e)

    def handle_aim_turret(self, opts):
        """Validate options and make call to gunner.

        :param opts: Dict with keys 'x' and 'y' (angles 0-180).
        :type opts: dict

        """
        # Validate x angle option
        try:
            x_angle = int(round(opts["x"]))
        except KeyError:
            return "Error: No 'x' opt given"
        except ValueError:
            return "Error: Unable to convert x to int"

        # Validate y angle option
        try:
            y_angle = int(round(opts["y"]))
        except KeyError:
            return "Error: No 'y' opt given"
        except ValueError:
            return "Error: Unable to convert y to int"

        # Make call to gunner
        try:
            self.gunner.aim_turret(x_angle=x_angle, y_angle=y_angle)
        except Exception as e:
            return "Error: {}".format(e)

    def handle_advance_dart(self):
        """Make call to gunner to advance a dart."""
        try:
            self.gunner.advance_dart()
        except Exception as e:
            return "Error: {}".format(e)

    def handle_fire_speed(self, opts):
        """Set rotation speed of firing wheels.

        :param opts: Dict with key 'speed' (0-100).
        :type opts: dict

        """
        # Validate speed option
        try:
            speed = int(round(opts["speed"]))
        except KeyError:
            return "Error: No 'speed' key given"
        except ValueError:
            return "Error: Unable to convert speed to int"

        # Make call to gunner
        try:
            self.gunner.wheel_speed = speed
        except Exception as e:
            return "Error: {}".format(e)

    def handle_die(self):
        """Accept poison pill and gracefully exit.

        Note that this method needs to print and send the reply itself,
        as it exits the process before listen() could take those actions.

        """
        print "Success: Received message to die. Bye!"
        self.socket.send("Success: Received message to die. Bye!")
        sys.exit(0)

if __name__ == "__main__":
    server = Server(testing=sys.argv[1])
    server.listen()
