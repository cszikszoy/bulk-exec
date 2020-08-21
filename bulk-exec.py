#!/usr/bin/python3

import re
import sys
import subprocess
from getpass import getpass
from os.path import expanduser

# get hosts from host list file
hosts = open(sys.argv[1], "r+").readlines()

# get commands from command list file
cmds = open(sys.argv[2], "r+").readlines()

# if any commands start with sudo, ask for password
if any(cmd.startswith('sudo ') for cmd in cmds):
    sudo_pwd = getpass("Enter sudo password:")

    # prepend any sudoo commands with -k -S -s and wrap it in quotes
    # -k expire timestamp so sudo asks for a password each time
    # -S no TTY (so we can enter a password)
    # -s execute using $SHELL
    # this will probably break if the actual command contains quotes...
    cmds = [re.sub('^sudo (.*)', rf'sudo -k -S -s "\1"\n{sudo_pwd}', cmd) for cmd in cmds]

# tell everyone what commands we're going to execute
print(f"Commands to execute:\n{cmds}\n")

# for each host in our host list file
for host in [h.strip() for h in hosts]:
    # tell everyone what host we're on
    print(f"Connecting to {host}...")

    # create a ssh subprocess, using the identity file in $HOME/.ssh/
    ssh = subprocess.Popen(["ssh", "-T", "-i", "{0}/.ssh/id_rsa".format(expanduser("~")), host],
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            universal_newlines = True,
                            bufsize = 0)

    # write all commands to stdin
    for cmd in cmds:
        ssh.stdin.write(cmd)

    # close stdin
    ssh.stdin.close()

    # read stdout
    output = ssh.stdout.readlines()

    # read stderr
    error = ssh.stderr.readlines()

    # print any errors
    if error != []:
        print("Errors:")
        print(*error)

    # print any output
    if output != []:
        print("Output:")
        print(*output)
