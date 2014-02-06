#!/usr/bin/env python
"""Start CLI or auto interfaces, CtrlServer or tests."""

import argparse
from subprocess import Popen
import signal
import os
import sys
from time import sleep

import lib.lib as lib
import interface.cli as cli_mod
import planner.fsm_planner as pfsm_mod

# Build parser and argument groups
description="start CLI, Planner, CtrlServer, unit tests or PEP8 scan"
parser = argparse.ArgumentParser(description)

# Starting interfaces should be mutually exclusive
interface_group = parser.add_mutually_exclusive_group()

# Add arguments
parser.add_argument("-T", "--test-mode", action="store_true",
    help="use simulated hardware, to allow running off the bone")
parser.add_argument("-8", "--pep8", action="store_true",
    help="run script to check PEP8 style conformance")
parser.add_argument("-t", "--tests", action="store_true",
    help="run all unit tests")
parser.add_argument("-s", "--server", action="store_true",
    help="start server to provide for controlling the bot")
interface_group.add_argument("-a", "--auto", action="store_true",
    help="autonomously solve the course")
interface_group.add_argument("-c", "--cli", action="store_true",
    help="CLI interface for controlling the bot")

# Print help if no arguments are given
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

# Parse the given args
args = parser.parse_args()

# Run on simulated hardware, or not
lib.set_testing(args.test_mode)
if args.test_mode:
    print "Using simulated hardware"

if args.pep8:
    print "Running PEP8 style checks"
    os.system("./scripts/check_pep8.sh")

if args.tests:
    print "Running unit tests"
    os.system("python -m unittest discover")

if args.server:
    # Fail if starting the server on the bot and not root
    if not args.test_mode and os.geteuid() != 0:
        print "Error: Running server in non-test mode requires root."
        sys.exit(1)

    # Function for server to run just before execution
    def preexec_fn():
        """Ignores SIGINT (ctrl+c)."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    print "Starting server"
    process_description = ["./server/ctrl_server.py", str(args.test_mode)]
    server = Popen(process_description, preexec_fn=preexec_fn)
    # Give server a chance to get up and running
    sleep(.3)

if args.auto:
    print "Starting autonomous solver"
    planner = pfsm_mod.Robot()

if args.cli:
    # Build addresses of remote resources
    config = lib.get_config("config.yaml")
    ctrl_addr = "{protocol}://{host}:{port}".format(
        protocol=config["server_protocol"],
        host=config["server_host"],
        port=config["ctrl_server_port"])
    sub_addr = "{protocol}://{host}:{port}".format(
        protocol=config["server_protocol"],
        host=config["server_host"],
        port=config["pub_server_port"])

    print "Starting CLI"
    try:
        cli_mod.CLI(ctrl_addr, sub_addr).cmdloop()
    except KeyboardInterrupt:
        print "Exiting CLI"
