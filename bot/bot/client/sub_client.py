"""Subscribe to data published by the bot."""

import sys
from pprint import pprint

try:
    import zmq
except ImportError:
    sys.stderr.write("ERROR: Failed to import zmq. Is it installed?")
    raise


class SubClient(object):

    """Use ZMQ SUB socket to get information about the bot.

    The SubClient is responsible for managing all interaction with PubServer,
    which publishes information about the state of the bot over a ZMQ SUB
    socket. Interfaces, like CLI, own clients like SubClient (and/or
    CtrlClient) and use them to interact with the servers (like PubServer
    and CtrlServer) running on the bot. The server own bot systems, like
    gunner and follower.

    """

    def __init__(self, sub_addr="tcp://127.0.0.1:60001"):
        """Build ZMQ subscriber socket and connect to PubServer.

        :param sub_addr: Address of PubServer, to subscribe to for topics.
        :type sub_addr: string

        """
        # Build ZMQ subscriber socket
        self.context = zmq.Context()
        self.sub_addr = sub_addr
        self.sub_sock = self.context.socket(zmq.SUB)
        self.sub_sock.connect(self.sub_addr)
        print "SubClient subscribed to PubServer at {}".format(self.sub_addr)

    def print_msgs(self):
        """Prints messages subscribed to via SUB socket.

        Note that crtl+c is the expected way to exit this loop.

        """
        print "Printing messages, ctrl+c to quit loop..."
        while True:
            try:
                pprint(self.sub_sock.recv())
            except KeyboardInterrupt:
                print
                return

    def add_topic(self, topic):
        """Set SUB socket to listen for the given topic.

        Note that the format of topics is a bit interesting. From what I can
        tell, any topic that matches the regex ^topic* will be subscribed
        to. For example, if there's a topic drive_motor_detail_br and another
        drive_motor_detail_fr, then passing drive_motor_detail will subscribe
        to both of them. On the other hand, passing motor_detail_fr will not
        subscribe to any topic (unless there's another one that starts with
        motor_detail_fr).

        Also note that with ZMQ (libzmq) >= 3.0, filtering of topics is done
        at the publisher. So, topics that are not subscribed to by any clients
        will not be published, reducing the load on the bot.

        :param topic: Topic to listen for.
        :type topic: string

        """
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, topic)

    def del_topic(self, topic):
        """Stop subscribing to the given topic via ZMQ's SUB socket.

        Note that the format of topics is a bit interesting. From what I can
        tell, any topic that matches the regex ^topic* will be subscribed
        to. For example, if there's a topic drive_motor_detail_br and another
        drive_motor_detail_fr, then passing drive_motor_detail will subscribe
        to both of them. On the other hand, passing motor_detail_fr will not
        subscribe to any topic (unless there's another one that starts with
        motor_detail).

        Also note that with ZMQ (libzmq) >= 3.0, filtering of topics is done
        at the publisher. So, topics that are not subscribed to by any clients
        will not be published, reducing the load on the bot.

        :param topic: Topic to stop listening for.
        :type topic: string

        """
        self.sub_sock.setsockopt(zmq.UNSUBSCRIBE, topic)

    def clean_up(self):
        """Tear down ZMQ socket."""
        self.sub_sock.close()
        self.context.term()
