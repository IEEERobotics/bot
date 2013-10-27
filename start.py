#!/usr/bin/env python
# Start various clients, server or tests

import sys
import getopt
from subprocess import Popen
import os
from time import sleep

import lib.lib as lib
import client.desktop_client as desktop_client_mod
import client.cli_client as cli_client_mod
import planner.fsm_planner as pfsm_mod


def main(argv):
    """Get arguments and handle them."""
    try:
        opts, args = getopt.getopt(argv, "hsdtp8xcT",
                     ["help", "server", "desktop", "tests", "planner",
                      "pep8", "exit-server", "cli", "test-mode"])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    opt_list = list(zip(*opts)[0])

    if len(opt_list) == 0 or "-h" in opt_list or "--help" in opt_list:
        print_help()
        sys.exit(0)

    if "-T" in opt_list or "--test-mode" in opt_list:
        test_mode = "True"
    else:
        test_mode = "False"
    lib.set_testing(bool(test_mode))

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
        server = Popen(["./server/server.py", test_mode])
        # Give server a chance to get up and running
        sleep(.2)

    if "-d" in opt_list or "--desktop" in opt_list:
        print "Starting desktop client."
        desktop_client_mod.DesktopClient().run()

    if "-c" in opt_list or "--cli" in opt_list:
        print "Starting CLI client."
        cli_client_mod.CLIClient().cmdloop()

    if "-x" in opt_list or "--exit-server" in opt_list:
        try:
            server.kill()
            print "Closed server"
        except NameError:
            print "I don't own the server. Use pkill/pgrep or similar."
    elif "-s" in opt_list or "--server" in opt_list:
        print "Server is still running, give -x to close next time."


def print_help():
    """Print usage of script."""
    print "start.py [-h|--help] [-s|--server] [-d|--desktop] [-t|--tests]\n" +\
          "         [-p|--planner] [-8|--pep8] [-x|--exit-server]"

if __name__ == "__main__":
    main(sys.argv[1:])
