"""Client for sending commands to the bot's server via CLI."""

import os
import sys

import lib.lib as lib
import server.server as server
import client
import cmd


class CLIClient(client.Client, cmd.Cmd):

    """Send user commands to ZMQ server running on the bot."""

    prompt = "bot$ "

    def __init__(self):
        """Connect to ZMQ server, general setup."""
        client.Client.__init__(self)
        cmd.Cmd.__init__(self)

    def help_help(self):
        """Provide help message for help command."""
        print "help [command]"
        print "\tProvide help on given command. If no param, list commands."

    def do_shell(self, cmd):
        """Allows normal shell commands to be run.

        :param cmd: Everything after "shell" or "!", to be passed to shell.
        :type cmd: string

        """
        os.system(cmd)

    def help_shell(self):
        """Provide help message for shell command."""
        print "!|shell [command]"
        print "\tSend command to underlying system shell (like Bash)."

    def do_EOF(self, line):
        """Cleans up when ctrl+d is used to exit client.

        :param line: Mandatory param for EOF handler, not used.
        :type line: string

        """
        self.cleanUp()
        print
        return True

    def help_EOF(self):
        """Provide help message for EOF (ctrl+d) command."""
        print "Exit the program with ctrl+d."

    def do_fire(self, raw_args):
        """Aim turret, set gun wheel speed, advance dart.

        :param raw_args: Command string with pitch, yaw and gun speed.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            pitch, yaw, speed = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Firing pitch: {}, yaw: {}, speed: {}".format(pitch,
                                                                       yaw,
                                                                       speed))
        # Issue commands to server
        self.send_aim(pitch, yaw)
        self.send_fire_speed(speed)
        self.send_advance_dart()

    def help_fire(self):
        """Provide help message for fire command."""
        print "fire <pitch> <yaw> <speed>"
        print "\tSet turret pitch (vertical) and yaw (horizontal) angle"
        print "\t(0-180), gun wheel speed (0-100) and fire dart."

    def do_auto_fire(self, raw_args):
        """Poll localizer for block, lookup targeting info, aim and fire.

        :param raw_args: Command string, unused.
        :type raw_args: string

        """
        self.send_fire()

    def help_auto_fire(self):
        """Provide help message for auto_fire command."""
        print "Autonomous firing routine. Asks localizer to use ultrasonic"
        print "\tsensors to find the block we're over, look up targeting"
        print "\tinformation, aim turret, set gun wheel speed and fire"

    def do_gun_speed(self, raw_args):
        """Set speed of gun motors as percent of max (0-100).

        :param raw_args: Command string with speed value.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            speed = raw_args.split()[0]
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Gun speed: {}".format(speed))
        # Issue commands to server
        self.send_fire_speed(speed)

    def help_gun_speed(self):
        """Provide help message for gun_speed command."""
        print "gun_speed <speed>"
        print "\tSpin gun wheels at given speed as percent of max (0-100)."

    def do_aim(self, raw_args):
        """Aim turret at given pitch and yaw.

        :param raw_args: Command string with pitch and yaw values.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            pitch, yaw = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Aiming pitch: {}, yaw: {}".format(pitch, yaw))
        # Issue commands to server
        self.send_aim(pitch, yaw)

    def help_aim(self):
        """Provide help message for aim command."""
        print "aim <pitch> <yaw>"
        print "\tSet turret to given pitch (vertical) and"
        print "\tyaw (horizontal) angles (0-180)."

    def do_push_dart(self, raw_args):
        """Push dart into gun wheels, making it fire.

        :param raw_args: Command string, unused.
        :type raw_args: string

        """
        self.logger.info("Advancing dart")
        # Issue commands to server
        self.send_fire()

    def help_push_dart(self):
        """Provide help message for push_dart command."""
        print "push_dart"
        print "\tAdvance dart into gun wheels."

    def do_fst(self, raw_args):
        """Move the bot at given forward, strafe and turn speeds.

        :param raw_args: Command string with forward, strafe and turn speeds.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            fwd, strafe, turn = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Moving fwd: {}, strafe: {}, turn: {}".format(fwd,
                                                                       strafe,
                                                                       turn))
        # Issue commands to server
        self.send_fwd_strafe_turn(fwd, strafe, turn)

    def help_fst(self):
        """Provide help message for fst (forward_strafe_turn) command."""
        print "fst <forward speed> <strafe speed> <turn speed>"
        print "\tSet bot to drive at the given speeds."

    def do_move(self, raw_args):
        """Move at the given speed (0-100) and angle (0-360).

        :param raw_args: Commands string with speed and angle values.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            speed, angle = raw_args.split()
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Moving speed: {}, angle: {}".format(speed, angle))
        # Issue commands to server
        self.send_move(speed, angle)

    def help_move(self):
        """Provide help message for move command."""
        print "move <speed> <angle>"
        print "\tTranslate the bot. Speed is percent of max (0-100), angle"
        print "\tis in degrees (0-360, 90=left, 270=right)."

    def do_rotate(self, raw_args):
        """Rotate the bot at the given signed speed.

        :param raw_args: Commands string with signed speed to rotate.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            speed = raw_args.split()[0]
        except ValueError:
            print "Invalid command, see help [cmd]."
            return

        self.logger.info("Rotate speed: {}".format(speed))
        # Issue commands to server
        self.send_rotate(speed)

    def help_rotate(self):
        """Provide help message for rotate command."""
        print "rotate <speed>"
        print "\tRotate at given speed (-100 to 100, + is counterclockwise)."

    def do_die(self, raw_args):
        """Disconnect from server and close client."""
        self.cleanUp()
        return True

    def help_die(self):
        """Provide help message for die command."""
        print "die"
        print "\tDisconnect from server and close client."

    def do_kill(self, raw_args):
        """Kill the server. Doesn't close client."""
        # Issue commands to server
        self.send_die()

    def help_kill(self):
        """Provide help message for kill command."""
        print "kill"
        print "\tKill the server. Doesn't close client."
