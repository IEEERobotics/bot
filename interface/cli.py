#!/usr/bin/env python
"""Send commands to the bot through a CLI interface."""

import cmd
import sys
import os

# These paths will need to be changed if this is running ouside of the repo
new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path
import client.ctrl_client as ctrl_client_mod
import client.sub_client as sub_client_mod


class CLI(cmd.Cmd):

    """CLI for interacting with the bot."""

    prompt = "bot$ "

    def __init__(self, ctrl_addr, sub_addr):
        """Connect to ZMQ server, general setup.

        We're not using a logger or config here to reduce dependencies.

        TODO(dfarrell07): better docstring

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
        """Handle dynamic command list retrieved from server.

        TODO(dfarrell07): better docstring

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        obj_name, _, rest = raw_args.partition(' ')
        if obj_name in self.ctrl_client.objects:
            method_name, _, params = rest.partition(' ')
            if method_name in self.ctrl_client.objects[obj_name]:
                try:
                    param_dict = {}
                    # Split param into its key:value strs and iterate on them.
                    for param in params.split():
                        # Split key:value param pair
                        key, value = param.split(":")

                        # We need to convert param's value, which was given to
                        # this method as a string in raw_args, to the type
                        # expected by the method it will be passed to.
                        # This is a dirty heuristic!
                        # Exported methods should be robust enough to deal
                        # with maybe-poorly converted params.

                        # Try converting to int/float - easy to know if wrong
                        try:
                            if "." in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            # It wasn't an int or float, assume string
                            # If user gave key:'value', strip '' chars
                            if value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            # It's already type string, no need to cast
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
        """Augment Cmd.completenames() to handle the object names received
        after querying the API.

        TODO(dfarrell07): Get first line to <=79, expand below if needed

        :param text: TODO
        :type text: TODO
        :param *ignored: TODO
        :type *ignored: TODO

        """
        # NB: we can't use super() here since Cmd is an old-style class
        names = cmd.Cmd.completenames(self, text, *ignored)
        api_names = [x for x in self.ctrl_client.objects.keys() if x.startswith(text)]
        return names + api_names

    def completedefault(self, text, line, begidx, endidx):
        """Handles completion of methods exported by API.

        The matching of the first term is done separately, using the results
        of Cmd.copmletenames()

        :param text: TODO
        :type text: TODO
        :param line: TODO
        :type line: TODO
        :param begidx: TODO
        :type begidx: TODO
        :param endidx: TODO
        :type endidx: TODO
        :returns: TODO

        """
        obj, _, rest = line.partition(' ')
        if obj in self.ctrl_client.objects:
            method, _, params = rest.strip().partition(' ')
            if method == text:  # FIXME: this should actually verify index postion
                methods = [x for x in self.ctrl_client.objects[obj] if x.startswith(text)]
                return methods

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

    def do_exit_ctrl(self, raw_args):
        """Send message to CtrlServer, asking it to exit.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        self.ctrl_client.exit_server()

    def help_exit_ctrl(self):
        """Provide help message for exit_ctrl command."""
        print "exit_ctrl"
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
