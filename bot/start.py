#!/usr/bin/env python
"""Start CLI, pilot and/or CtrlServer."""

import argparse
from subprocess import Popen
import signal
import os
import sys
from time import sleep

# Always called on startup, make sure it's actually ready
new_path = [os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")]
sys.path = new_path + sys.path

import lib.lib as lib
import interface.cli as cli_mod

# Build parser and argument groups
description = "start CLI, pilot and/or CtrlServer"
parser = argparse.ArgumentParser(description)

# Starting interfaces should be mutually exclusive
interface_group = parser.add_mutually_exclusive_group()

# Add arguments
parser.add_argument(
    "-T", "--test-mode", action="store_true",
    help="use simulated hardware, to allow running off the bone")
parser.add_argument(
    "-s", "--server", action="store_true",
    help="start server to provide for controlling the bot")
interface_group.add_argument(
    "-p", "--pilot", action="store_true",
    help="autonomously solve the course")
interface_group.add_argument(
    "-c", "--cli", action="store_true",
    help="CLI interface for controlling the bot")

# Print help if no arguments are given
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

# Parse the given args
args = parser.parse_args()

# Run on simulated hardware, or not
lib.set_testing(args.test_mode, "config.yaml")
if args.test_mode:
    print "Using simulated hardware"

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
    # Need to have process start from root of repo for imports to work
    cwd = str(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
    process_description = ["./bot/server/ctrl_server.py", str(args.test_mode)]
    server = Popen(process_description, preexec_fn=preexec_fn, cwd=cwd)
    # Give server a chance to get up and running
    sleep(.3)

if args.pilot:
    import pilot as pilot_mod
    print "Starting pilot"
    pilot = pilot_mod.Pilot()
    pilot.run()

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
