#!/usr/bin/env python 
"""Send commands to the bot through a CLI interface."""

import cmd
import sys

import client.ctrl_client as ctrl_client_mod
import client.sub_client as sub_client_mod


class CLI(cmd.Cmd):

    """CLI for interacting with the bot."""

    prompt = "bot$ "

    def __init__(self, ctrl_addr, sub_addr):
        """Connect to ZMQ server, general setup.

        We're not using a logger or config here to reduce dependencies.

        :param ctrl_addr: Address of control server to connect to via ZMQ.
        :type ctrl_addr: string
        :param sub_addr: Address of PUB/SUB server to connect to via ZMQ.
        :type sub_addr: string

        """
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

        # Call superclass __init__
        cmd.Cmd.__init__(self)

    def default(self, raw_args):
        """Handle dynamic command list retrieved from server.

        :param raw_args: Mandatory param for Cmd handler, not used.
        :type raw_args: string

        """
        try:
            obj_name,_,rest = raw_args.partition(' ')
        except ValueError:
            # Tried to split raw_args with only a single word
            return
        if obj_name in self.ctrl_client.objects:
            method_name,_,params = rest.partition(' ')
            if method_name in self.ctrl_client.objects[obj_name]:
                try:
                    def str2param(s):
                        """Quick and dirty heuristic-based string conversion.

                        :param s: TODO
                        :type s: TODO

                        """
                        if s.startswith("'") and s.endswith("'"):
                            return s[1:-1]
                        elif '.' in s:
                            return float(s)
                        return int(s)
                    # TODO(dfarrell07): Document this line, maybe make multi-line
                    param_dict = {p.split(':')[0]: str2param(p.split(':')[1]) for p in params.split()} 
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
        api_names = [x for x in self.api.objects.keys() if x.startswith(text)]
        return names + api_names

    # NB: The matching of the first term is done separately, using the results
    # of Cmd.copmletenames()
    def completedefault(self, text, line, begidx, endidx):
        # TODO(dfarrell07): Add docstring
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
        reply, reply_time = self.ctrl_client.ping()
        if reply["type"] == "ctrl_success":
            print "Ctrl server response time:", reply_time*1000, "ms"
        else:
            print "Error: {}".format(reply)

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
        CLI('tcp://localhost:60000').cmdloop()
    elif ':' in sys.argv[1]:
        CLI('tcp://{}'.format(sys.argv[1])).cmdloop()
    else:
        CLI('tcp://{}:60000'.format(sys.argv[1])).cmdloop()
