#!/usr/bin/env python 
"""Send commands to the bot's API server through a generated CLI interface."""

import cmd
import sys

import api_client
import sub_client
import client


class CLIClient(cmd.Cmd):

    """Simple CLI client to the ZMQ API server running on the bot."""

    prompt = "bot$ "

    def __init__(self, api_addr, sub_addr, topic_addr):
        """Connect to ZMQ server, general setup.

        :param api_addr: Adderess of ZMQ server to connect to.
        :type api_addr: string
        TODO

        """
        # Build API client
        try:
            self.api = api_client.ApiClient(api_addr)
        except Exception, e:
            print "Couldn't build ApiClient addr:{} e:{}".format(api_addr, e)
            sys.exit(-1)

        # Build sub client
        try:
            self.sub_client = sub_client.SubClient(sub_addr, topic_addr)
        except Exception, e:
            print "SubClient error sub_addr:{} topic_addr:{}, e:{}".format(
                                                sub_addr, topic_addr, e)
            sys.exit(-1)

        # Call superclass __init__
        cmd.Cmd.__init__(self)

    def default(self, line):
        """Handle dynamic command list retrieved from server.

        :param line: Mandatory param for Cmd handler, not used.
        :type line: string

        """
        try:
            obj_name,_,rest = line.partition(' ')
        except ValueError:
            # Tried to split line with only a single word
            return
        if obj_name in self.api.objects:
            method_name,_,params = rest.partition(' ')
            if method_name in self.api.objects[obj_name]:
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
                result = self.api.call(obj_name, method_name, param_dict)
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
        if obj in self.api.objects:
            method, _, params = rest.strip().partition(' ')
            if method == text:  # FIXME: this should actually verify index postion
                methods = [x for x in self.api.objects[obj] if x.startswith(text)]
                return methods

    def do_list(self, line):
        """Provide a list of bot API objects and their methods.

        :param line: Mandatory param for Cmd handler, not used.
        :type line: string

        """
        print
        print "Available bot objects and methods"
        print
        for obj_name, methods in sorted(self.api.objects.items()):
            print "{}:".format(obj_name)
            for method in methods:
                print "    - {}".format(method)
        print

    def do_ping(self, line):
        """Ping the remote server API on the bot.

        :param line: Mandatory param for Cmd handler, not used.
        :type line: string

        """
        reply, reply_time = self.api.ping()
        if reply['status'] == 'success':
            print "API response time:", reply_time*1000, "ms"
        else:
            print "Error: {}".format(reply)

    def do_pub_add(self, raw_args):
        """Set topics for PubServer to publish.

        :param raw_args: Commands string with topic name to add.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            topic = raw_args.split()[0]
        except (ValueError, IndexError):
            print "Invalid command, see help [cmd]."
            return

        print "New pub topic: {}".format(topic)
        # Issue commands to server
        self.sub_client.add_topic(topic)

    def help_pub_add(self):
        """Provide help message for pub_add command."""
        print "pub_add <topic>"
        print "\tTell PubServer to start publishing this topic."

    def do_pub_del(self, raw_args):
        """Delete topics that PubServer is publishing.

        :param raw_args: Commands string with topic name to delete.
        :type raw_args: string

        """
        # Get and validate arguments
        try:
            topic = raw_args.split()[0]
        except (ValueError, IndexError):
            print "Invalid command, see help [cmd]."
            return

        print "Deleting pub topic: {}".format(topic)
        # Issue commands to server
        self.sub_client.del_topic(topic)

    def help_pub_del(self):
        """Provide help message for pub_del command."""
        print "pub_del <topic>"
        print "\tTell PubServer to stop publishing this topic."

    def do_die(self, raw_args):
        """Disconnect from server and close client."""
        print "Disconnecting..."
        self.api.cleanUp()
        print "Bye!"
        return True

    def help_die(self):
        """Provide help message for die command."""
        print "die"
        print "\tDisconnect from server and close client."

    def do_EOF(self, line):
        """Cleans up when ctrl+d is used to exit client.

        :param line: Mandatory param for Cmd handler, not used.
        :type line: string

        """
        print "Disconnecting..."
        self.api.cleanUp()
        print "Bye!"
        return True

    def help_EOF(self):
        """Provide help message for EOF (ctrl+d) command."""
        print "Exit the program with ctrl+d."


if __name__ == '__main__':
    if len(sys.argv) == 1:
        CLIClient('tcp://localhost:60000').cmdloop()
    elif ':' in sys.argv[1]:
        CLIClient('tcp://{}'.format(sys.argv[1])).cmdloop()
    else:
        CLIClient('tcp://{}:60000'.format(sys.argv[1])).cmdloop()
