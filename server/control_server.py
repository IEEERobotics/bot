#!/usr/bin/env python
"""Server for handling interaction between clients and bot."""

import sys
import os
from time import sleep
from math import fabs
import traceback
from inspect import getmembers, ismethod
from simplejson.decoder import JSONDecodeError

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise

new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import gunner.wheel_gunner as wg_mod
import follower.follower as f_mod
import server.server as server
import pub_server as pub_server_mod


class ControlServer(server.Server):

    """Listen for client commands and make them happen on the bot."""

    def __init__(self, testing=None):
        """Build all main bot objects, set ZMQ to listen."""
        # Call superclass __init__
        server.Server.__init__(self)
        
        # Load configuration and logger
        self.config = lib.load_config()
        self.logger = lib.get_logger()

        # Testing flag will cause objects to run on simulated hardware
        if testing == "True":
            self.logger.info("ControlServer running in test mode")
            lib.set_testing(True)
        elif testing == "False":
            self.logger.info("ControlServer running in non-test mode")
            lib.set_testing(False)
        else:
            self.logger.info("Defaulting to config testing flag: {}".format(
                                                    self.config["testing"]))
            lib.set_testing(self.config["testing"])

        # Build socket to listen for requests
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.server_bind_addr = "{protocol}://{host}:{port}".format(
            protocol=self.config["server_protocol"],
            host=self.config["server_bind_host"],
            port=self.config["server_port"])
        self.socket.bind(self.server_bind_addr)

        # Build WheelGunner, which will accept and handle fire actions
        self.gunner = wg_mod.WheelGunner()

        # Build follower, which will manage following line
        self.follower = f_mod.Follower()
        self.driver = self.follower.driver

        # Build context object, containing bot resources
        context = self.build_context()

        # Spawn PubServer for publishing bot data
        self.spawn_pub_server(context)

    def listen(self):
        """Listen for messages, pass them off to be handled and send reply."""
        self.logger.info("ControlServer listening on {}".format(
                                                self.server_bind_addr))
        while True:
            try:
                # Receive JSON-formated message as a dict
                msg = self.socket.recv_json()
                self.logger.debug("Received: {}".format(msg))

                # Handle message, send reply
                reply_msg = self.on_message(msg)
                self.logger.debug("Replying: {}".format(reply_msg))
                self.socket.send_json(reply_msg)
            except JSONDecodeError:
                error_msg = "Non-JSON message"
                self.logger.error(error_msg)
                self.socket.send_json(self.build_reply("Error", msg=error_msg))
            except KeyboardInterrupt:
                self.handle_die()
            except Exception as e:
                error_msg = str(e)
                self.logger.error(error_msg)
                self.socket.send_json(self.build_reply("Error", msg=error_msg))

    def build_context(self):
        """Builds standard object to store resources.

        :returns: Context, which stores standard objects like gunner, gun...

        """
        context = {}
        context["gunner"] = self.gunner
        context["follower"] = self.follower
        context["driver"] = self.follower.driver
        context["turret"] = self.gunner.turret
        context["gun"] = self.gunner.gun
        context["ir_hub"] = self.follower.ir_hub
        return context

    def spawn_pub_server(self, context):
        """Spawn publisher thread, passing it common bot objects.

        :param context: Common objects used by the bot.
        :type context: dict

        """
        self.pub_server = pub_server_mod.PubServer(context)
        # Prevent pub_server thread from blocking the process from closing
        self.pub_server.setDaemon(True)
        self.pub_server.start()

    def handle_fwd_strafe_turn(self, opts):
        """Validate options and make move call to driver.

        Speed should be between 0-100, angle between 0-360.

        :param opts: Dict with keys 'speed' and 'angle' to move.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate fwd option
        try:
            fwd = float(opts["fwd"])
        except KeyError:
            return self.build_reply("Error", msg="No 'fwd' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert fwd to float")

        # Validate strafe option
        try:
            strafe = float(opts["strafe"])
        except KeyError:
            return "Error: No 'strafe' opt given"
            return self.build_reply("Error", msg="No 'strafe' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert strafe to float")

        # Validate turn option
        try:
            turn = float(opts["turn"])
        except KeyError:
            return self.build_reply("Error", msg="No 'turn' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert turn to float")

        # Make call to driver
        try:
            # Rotate only when turn dominates
            if fabs(turn) > fabs(fwd) and fabs(turn) > fabs(strafe):
                self.driver.rotate(turn)
            else:
                self.driver.move_forward_strafe(fwd, strafe)
        except Exception:
            tb = traceback.format_exc()
            return self.build_reply("Error", msg=tb)

        return self.build_reply("Success", result=opts)

    def handle_move(self, opts):
        """Validate options and make move call to driver.

        Speed should be between 0-100, angle between 0-360.

        :param opts: Dict with keys 'speed' and 'angle' to move.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate speed option
        try:
            speed = float(opts["speed"])
        except KeyError:
            return self.build_reply("Error", msg="No 'speed' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert speed to float")

        # Validate angle option
        try:
            angle = float(opts["angle"])
        except KeyError:
            return self.build_reply("Error", msg="No 'angle' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert angle to float")

        # Make call to driver
        try:
            self.driver.move(speed=speed, angle=angle)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

        return self.build_reply("Success", result=opts)

    def handle_rotate(self, opts):
        """Validate options and make rotate call to driver.

        :param opts: Dict with key 'speed' to rotate, -100 to 100.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate speed option
        try:
            rotate_speed = float(opts["speed"])
        except KeyError:
            return self.build_reply("Error", msg="No 'speed' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert speed to float")

        # Make call to driver
        try:
            self.driver.rotate(rotate_speed=rotate_speed)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

        return self.build_reply("Success", result=opts)

    def handle_auto_fire(self, opts):
        """Make fire call to gunner. Normally used in autonomous mode.

        :returns: success or error message with description.

        """
        # Make call to gunner
        try:
            self.gunner.auto_fire()
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

        return self.build_reply("Success", result="Fired")

    def handle_aim(self, opts):
        """Validate options and make call to gunner.

        :param opts: Dict with keys 'x' and 'y' (angles 0-180).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate yaw angle option
        try:
            yaw = int(round(float(opts["yaw"])))
        except KeyError:
            return self.build_reply("Error", msg="No 'yaw' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert yaw to int")

        # Validate pitch angle option
        try:
            pitch = int(round(float(opts["pitch"])))
        except KeyError:
            return self.build_reply("Error", msg="No 'pitch' opt given")
        except ValueError:
            return self.build_reply("Error",
                                    msg="Could not convert pitch to int")

        # Make call to gunner
        try:
            self.gunner.aim_turret(yaw, pitch)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

        return self.build_reply("Success", result=opts)

    def handle_fire_speed(self, opts):
        """Set rotation speed of firing wheels.

        :param opts: Dict with key 'speed' (0-100).
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # TODO: Add once capes are installed
        return self.build_reply("Error", msg="Not yet implemented")

        # Validate speed option
        try:
            speed = int(round(float(opts["speed"])))
        except KeyError:
            return self.build_reply("Error", msg="No 'speed' opt given")
        except TypeError:
            return self.build_reply("Error",
                                    msg="Could not convert speed to int")

        # Make call to gunner
        try:
            self.gunner.gun.wheel_speed = speed
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

        return self.build_reply("Success", result=opts)

    def handle_laser(self, opts):
        """Turn laser ON or OFF.

        :param opts: Dict with key 'state' (0/1).
        :type opts: dict
        :returns: A dict with result = laser state or error message.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate state option
        try:
            state = int(round(float(opts["state"])))
        except KeyError:
            return self.build_reply("Error", msg="No 'state' opt given")
        except TypeError:
            return self.build_reply("Error",
                                    msg="Could not convert state to int")

        # Make call to gun
        try:
            result = self.gunner.gun.laser = state
            return self.build_reply("Success", result=result)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

    def handle_spin(self, opts):
        """Turn gun motor spin ON or OFF.

        :param opts: Dict with key 'state' (0/1).
        :type opts: dict
        :returns: A dict with result = spin state or error message.

        """
        # Validate that opts key was given
        if opts is None:
            return self.build_reply("Error",
                                    msg="opts key required for this cmd")

        # Validate state option
        try:
            state = int(round(float(opts["state"])))
        except KeyError:
            return self.build_reply("Error", msg="No 'state' opt given")
        except TypeError:
            return self.build_reply("Error",
                                    msg="Could not convert state to int")

        # Make call to gun
        try:
            result = self.gunner.gun.spin = state
            return self.build_reply("Success", result=result)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

    def handle_fire(self, opts=None):
        """Make fire call to gun, using default parameters.

        :param opts: Ignored.
        :type opts: dict
        :returns: Success or error message with description.

        """
        # Make call to gun
        try:
            result = self.gunner.gun.fire()
            return self.build_reply("Success", result=result)
        except Exception as e:
            return self.build_reply("Error", msg=str(e))

    def handle_die(self, opts=None):
        """Accept poison pill and gracefully exit.

        :param opts: Ignored.
        :type opts: dict
        :returns: Success or error message with description.

        Note that this method needs to print and send the reply itself,
        as it exits the process before listen() could take those actions.
        TODO: Instead, use an 'is_alive' flag in listen() for clean exit.

        """
        self.logger.info("Success: Received message to die. Bye!")
        reply = self.build_reply("Success",
                                 msg="Received message to die. Bye!")
        self.socket.send_json(reply)
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        server = ControlServer(sys.argv[1])
    else:
        server = ControlServer()
    server.listen()
