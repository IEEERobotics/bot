#!/usr/bin/env python
# Start various clients, server or tests

import sys
import argparse
from subprocess import Popen
import os
from time import sleep

import lib.lib as lib
import client.desktop_client as desktop_client_mod
import client.cli_client as cli_client_mod
import client.sub_client as sub_client_mod
import planner.fsm_planner as pfsm_mod

# Build parser and argument groups
parser = argparse.ArgumentParser(description="start bot clients, servers and tests")
root_group = parser.add_mutually_exclusive_group()
client_group = root_group.add_mutually_exclusive_group()
test_group = root_group.add_mutually_exclusive_group()

# Add arguments
client_group.add_argument("-a", "--auto-client", action="store_true",
                          help="autonomously solve the course")
client_group.add_argument("-c", "--cli-client", action="store_true",
                          help="CLI interface for controlling the bot")
client_group.add_argument("-d", "--desktop-client", action="store_true",
                          help="desktop GUI interface for controlling the bot")
client_group.add_argument("-u", "--sub-client", action="store_true",
                          help="subscribe to bot's published information")
test_group.add_argument("-t", "--tests", action="store_true",
                        help="run all unit tests")
test_group.add_argument("-8", "--pep8", action="store_true",
                        help="run script to check PEP8 style conformance")
parser.add_argument("-T", "--test-mode", action="store_true",
                    help="use simulated hardware, to allow running off the bone")
parser.add_argument("-s", "--server", action="store_true",
                    help="start server to provide interface for controlling the bot")
parser.add_argument("-p", "--pub-server", action="store_true",
                    help="start server to publish bot's information")

# Parse the given args
args = parser.parse_args()

# Run on simulated hardware or not
lib.set_testing(args.test_mode)

if args.test_mode:
    print "Using simulated hardware"
else:
    print "Using real hardware. Hopefully you're on a bone."

if args.pep8:
    print "Running PEP8 style checks"
    os.system("./scripts/check_pep8.sh")

if args.tests:
    print "Running unit tests"
    os.system("python -m unittest discover")

if args.auto_client:
    print "Starting autonomous client"
    planner = pfsm_mod.Robot()

if args.server:
    print "Starting server"
    server = Popen(["./server/server.py", str(args.test_mode)])
    # Give server a chance to get up and running
    sleep(.2)

if args.pub_server:
    print "Starting PubServer"
    pub_server = Popen(["./server/pub_server.py", str(args.test_mode)])
    # Give server a chance to get up and running
    sleep(.2)

if args.cli_client:
    print "Starting CLI client"
    cli_client_mod.CLIClient().cmdloop()

if args.desktop_client:
    print "Starting desktop client"
    desktop_client_mod.DesktopClient().run()

if args.sub_client:
    print "Starting subscriber client"
    sub_client_mod.SubClient().print_msgs()
