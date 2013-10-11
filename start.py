#!/usr/bin/env python
# Start various clients, server or tests

import sys
import getopt
from subprocess import Popen
import os

import lib.lib
import client.desktop_client as desktop_client_mod
import planner.fsm_planner as pfsm_mod


def main(argv):
    """Get arguments and handle them."""
    try:
        opts, args = getopt.getopt(argv, "hsdtp8x",
                     ["help", "server", "desktop", "tests", "planner",
                      "pep8", "exit-server"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    opt_list = list(zip(*opts)[0])

    if len(opt_list) == 0 or "-h" in opt_list or "--help" in opt_list:
        print_help()
        sys.exit(0)

    if "-8" in opt_list or "--pep8" in opt_list:
        os.system("./scripts/check_pep8.sh")

    if "-t" in opt_list or "--tests" in opt_list:
        print "Running unit tests"
        os.system("python -m unittest discover")

    if "-p" in opt_list or "--planner" in opt_list:
        print "Starting planner"
        planner = pfsm_mod.Robot()

    if "-s" in opt_list or "--server" in opt_list:
        print "Starting server"
        server = Popen(["./server/server.py", "True"])

    if "-d" in opt_list or "--desktop" in opt_list:
        print "Starting desktop controller"
        desktop_client_mod.DesktopControlClient().run()

    if "-x" in opt_list or "--exit-server" in opt_list:
        print "Closing server"
        server.kill()
    elif "-s" in opt_list or "--server" in opt_list:
        print "Server is still running, give -x to close next time."


def print_help():
    """Print usage of script."""
    print "start.py [-h|--help] [-s|--server] [-d|--desktop]"

if __name__ == "__main__":
    main(sys.argv[1:])
