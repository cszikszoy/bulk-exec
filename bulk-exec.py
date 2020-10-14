#!/usr/bin/python3

import re
import sys
import subprocess
from getpass import getpass
from os.path import expanduser

def strip_comments(list):
    """Take list of commands as args, return list of commands minus any comment lines (starting with #)."""
    return [i for i in list if not i.startswith('#')]

# get hosts from host list file
hosts = open(sys.argv[1], "r+").readlines()

# strip any comments from the hosts file
hosts = strip_comments(hosts)

# get commands from command list file
cmds = open(sys.argv[2], "r+").readlines()

# strip any comments from the commands file
cmds = strip_comments(cmds)

# get $HOME
home = expanduser("~")

# tell everyone what commands we're going to execute
print(f"Commands to execute:\n{cmds}\n")

# if any commands start with sudo, ask for password
if any(cmd.startswith('sudo ') for cmd in cmds):
    sudo_pwd = getpass("Enter sudo password:")

    # prepend any sudoo commands with -k -S -s and wrap it in quotes
    # -k:       expire timestamp so sudo asks for a password each time
    # -S:       no TTY (so we enter a password on stdin)
    # sh -c:    execute with a shell (this allows commands to use pipes)
    #
    # this will probably break if the actual command contains quotes...
    cmds = [re.sub('^sudo (.*)', rf'sudo -k -S sh -c "\1"\n{sudo_pwd}', cmd) for cmd in cmds]

# for each host in our host list file
for host in [h.strip() for h in hosts]:
    # tell everyone what host we're on
    print(f"Connecting to {host}...")

    # create a ssh subprocess, using the identity file in $HOME/.ssh/
    ssh = subprocess.Popen(["ssh", "-T", "-i", f"{home}/.ssh/id_rsa", host],
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
