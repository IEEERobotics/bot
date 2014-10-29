#!/usr/bin/env python
"""Send commands to the bot through a CLI interface."""

import cmd
import sys
import os

import bot.client.ctrl_client as ctrl_client_mod
import bot.client.sub_client as sub_client_mod


class CLI(cmd.Cmd):

    """CLI for interacting with the bot.

    Note that the architecture is that interfaces, like the Command
    Line *Interface*, are used by agents like humans to interact
    with the bot. For interfaces to communicate with the bot, they
    own clients (like CtrlClient and SubClient), which know how to
    speak ZMQ to the servers (like CtrlServer and PubServer) running on
    the bot. Servers own systems (like gunner and driver) and known how
    to fire commands off to those systems and/or share data about their
    state.

    """

    prompt = "bot$ "

    def __init__(self, ctrl_addr, sub_addr):
        """Build CtrlClient and SubClient, for connections to servers.

        We're not using a logger or config here to reduce dependencies.

        CtrlClient is used for sending commands to the bot. Some commands,
        like `ping`, are answered by CtrlClient directly. Others, like
        `fire`, are actually exported methods that CtrlClient exposes
        via the API. Those calls are passed to the relevant method of a
        system owned by CtrlClient.

        SubClient manages subscriptions to topics published by PubServer
        on the bot. Topics can be subscribed to via `sub_add` and removed
        via `sub_del`. To print the data being published, use `sub`.
        Only topics that are actually subscribed to by one or more clients
        will be published by PubServer, saving bot resources. Note that
        PubServer isn't spawned by default when CtrlServer is created.
        To spawn it (in its own thread), issue `ctrl spawn_pub_server`.

        :param ctrl_addr: Address of control server to connect to via ZMQ.
        :type ctrl_addr: string
        :param sub_addr: Address of PUB/SUB server to connect to via ZMQ.
        :type sub_addr: string

        """
        # Call superclass __init__
        cmd.Cmd.__init__(self)

        # Build control client
        try:
            self.ctrl_client = ctrl_client_mod.CtrlClient(ctrl_addr)
        except Exception, e:
            print "Couldn't build CtrlClient addr:{} e:{}".format(ctrl_addr, e)
            sys.exit(-1)

        # Build sub client
        try:
            self.sub_client = sub_client_mod.SubClient(sub_addr)
        except Exception, e:
            print "SubClient error sub_addr:{}, error:{}".format(sub_addr, e)
            sys.exit(-1)

    def default(self, raw_args):
        """Parses API commands (ex `ctrl echo msg:7`) into calls to CtrlServer.

        API commands are those given by the `list` command. Note that a
        heuristic is used to convert params (like "7" in the example above)
        into the types expected by the method that will be called and passed
        that param by CtrlServer. It has held up well so far.

        :param raw_args: Command from user to be parsed/passed to CtrlServer.
        :type raw_args: string

        """
        obj_name, _, rest = raw_args.partition(" ")
        if obj_name in self.ctrl_client.objects:
            method_name, _, params = rest.partition(" ")
            if method_name in self.ctrl_client.objects[obj_name]:
                try:
                    param_dict = {}
                    # Split param into its key:value strs and iterate on them
                    for param in params.split():
                        # Split key:value param pair
                        key, value = param.split(":")

                        # We need to convert param's value, which was given to
                        # this method as a string in raw_args, to the type
                        # expected by the method it will be passed to.
                        # This is a dirty heuristic (that so far works well)!

                        # Try converting to int/float - easy to know if wrong
                        try:
                            if "." in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            # It wasn't an int or float, assume string or bool
                            # Check if bool
                            if value == "True":
                                value = True
                            elif value == "False":
                                value = False
                            # If user gave key:'value', strip '' chars
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            # Either bool or string at this point
                        param_dict[key] = value
                except IndexError:
                    print "Bad parameter list"
                    return
                except ValueError:
                    print "Bad parameter value"
                    return
                result = self.ctrl_client.call(obj_name, method_name, param_dict)
                print "-->", result
            else:
                print "Unknown API method:", method_name
        else:
            print "Unknown command:", obj_name

    def completenames(self, text, *ignored):
        """Handles tab-completion of object names exported by the API.

        Object names, like those returned by `list` (driver, gun...),
        aren't known to Cmd.completenames. We extend it here to deal
        with tab-completing them.

        :param text: Text the user has type so far, to be tab-completed.
        :type text: string
        :param *ignored: Not documented in Cmd.completenames. No idea.
        :type *ignored: Not documented in Cmd.completenames. Dict?

        """
        # NB: We can't use super() here since Cmd is an old-style class
        # Gets list of do_* methods that match what the user has typed so far
        cmd_match_names = cmd.Cmd.completenames(self, text, *ignored)

        # Need to do the same thing for exported API methods
        # Names of objects exported by API (like driver, gunner...)
        obj_names = self.ctrl_client.objects.keys()
        # Build list of obj_names that start with text given by user
        api_match_names = [x for x in obj_names if x.startswith(text)]
        return cmd_match_names + api_match_names

    def completedefault(self, text, line, begidx, endidx):
        """Handles tab-completion of method names exported by API.

        The matching of the first term (the object name exported by the API)
        is done separately, using the results of copmletenames().

        :param text: Part of method name (second arg) typed so far by user.
        :type text: string
        :param line: Entire line typed so far by user.
        :type line: string
        :param begidx: Index into "line" where "text" begins.
        :type begidx: int
        :param endidx: Index into "line" where "text" ends.
        :type endidx: int
        :returns: List of exported API methods that match text given by user.

        """
        obj, _, rest = line.partition(" ")
        if obj in self.ctrl_client.objects:
            # If the user tries to tab-complete once they have typed
            # `obj method par..`, "par.." being the start of a param, this
            # line will grab the method name only, dropping the param. We
            # can't tab-complete params at the moment (but that would be nice).
            method, _, params = rest.strip().partition(" ")
            # Only does this if user is tab-completing method, not params
            if method == text:  # FIXME: Should actually verify index position
                method_names = self.ctrl_client.objects[obj]
                match_names = [x for x in method_names if x.startswith(text)]
                return match_names

    def do_list(self, raw_args):
        """Provide a list of bot API objects and their methods.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        print
        print "Available bot objects and methods"
        print
        for obj_name, methods in sorted(self.ctrl_client.objects.items()):
            print "{}:".format(obj_name)
            for method in methods:
                print "    - {}".format(method)
        print

    def help_list(self):
        """Provide help message for list command."""
        print "list"
        print "\tList on-bot objects and methods exposed by the API."

    def do_ping(self, raw_args):
        """Ping the control server on the bot.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        reply_time = self.ctrl_client.ping()
        print "CtrlServer response time: {}ms".format(reply_time)

    def help_ping(self):
        """Provide help message for ping command."""
        print "ping"
        print "\tPing the control server on the bot."

    def do_sub_add(self, raw_args):
        """Subscribe to a published topic.

        Note that with ZMQ (libzmq) versions >= 3.0, topics that are not
        subscribed to by any client are not published (done automatically
        at the server).

        :param raw_args: Commands string with topic name to add.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            topic = raw_args.split()[0]
        except (ValueError, IndexError):
            print "Invalid command, see help [cmd]."
            return
        self.sub_client.add_topic(topic)

    def help_sub_add(self):
        """Provide help message for sub_add command."""
        print "sub_add <topic>"
        print "\tSubscribe to a published topic."

    def do_sub_del(self, raw_args):
        """Unsubscribe from a published topic.

        Note that with ZMQ (libzmq) versions >= 3.0, topics that are not
        subscribed to by any client are not published (done automatically
        at the server).

        :param raw_args: Commands string with topic name to unsubscribe from.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            topic = raw_args.split()[0]
        except (ValueError, IndexError):
            print "Invalid command, see help [cmd]."
            return
        self.sub_client.del_topic(topic)

    def help_sub_del(self):
        """Provide help message for sub_del command."""
        print "sub_del <topic>"
        print "\tUnsubscribe from a published topic."

    def do_sub(self, raw_args):
        """Print topics subscribed to via SubClient.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        self.sub_client.print_msgs()

    def help_sub(self):
        """Provide help message for sub command."""
        print "sub"
        print "\tPrint messages subscribed to. Ctrl+c to exit."

    def do_stop(self, raw_args):
        """Stop all drive and gun motors, put turret in save state.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        self.ctrl_client.stop_full()

    def help_stop(self):
        """Provide help message for stop command."""
        print "stop"
        print "\tStop all drive and gun motors, put turret in safe state."

    def do_kill(self, raw_args):
        """Send message to CtrlServer, asking it to exit.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        self.ctrl_client.exit_server()

    def help_kill(self):
        """Provide help message for kill command."""
        print "kill"
        print "\tAsk the CtrlServer to exit."

    def do_die(self, raw_args):
        """Disconnect from servers and close CLI.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        print "Disconnecting..."
        self.ctrl_client.clean_up()
        self.sub_client.clean_up()
        print "Bye!"
        return True

    def help_die(self):
        """Provide help message for die command."""
        print "die"
        print "\tDisconnect from servers and close CLI."

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

    def do_EOF(self, raw_args):
        """Cleans up when ctrl+d is used to exit client.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        print "Disconnecting..."
        self.ctrl_client.clean_up()
        self.sub_client.clean_up()
        print "Bye!"
        return True

    def help_EOF(self):
        """Provide help message for EOF (ctrl+d) command."""
        print "ctrl+d"
        print "\tDisconnect from servers and close CLI with ctrl+d."

    def help_help(self):
        """Provide help message for help command."""
        print "help [command]"
        print "\tProvide help on given command. If no argument, list commands."


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "No ctrl_addr or sub_addr given, using tcp://localhost:60000,1"
        CLI("tcp://localhost:60000", "tcp://localhost:60001").cmdloop()
    elif len(sys.argv) == 3:
        # Using given ctr_addr and sub_addr
        ctrl_addr = sys.argv[1]
        sub_addr = sys.argv[2]
        CLI(ctrl_addr, sub_addr).cmdloop()
    else:
        print "Error: Expected `./cli.py [ctrl_addr sub_addr]`"
