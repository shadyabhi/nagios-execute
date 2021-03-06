#!/usr/bin/python2

"""
Usage:

python2 script.py pwmail-mss 'date'

Make a file called config.py in the same directory as this script with contents similar to this


from os import environ as getenv

config = {
    'username' : "abhijeet.ras",

    'keyname' : "id_rsa_directi",
    'nagios_configs' : "./objects/hosts/",
    'parallel_procs' : 100,
}

config['keyfile'] = getenv['HOME'] + "/.ssh/" + config['keyname']
"""

import paramiko
import os
import sys
from multiprocessing import Pool, Lock
from config import config
import signal

#Some helper functions
def _wrap_with(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c 
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')

paramiko.util.log_to_file('ssh.log')

def execute_on_host((hostname, command), username=config['username'], keyfile=config['keyfile']):

    global lock
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=hostname, username=username, key_filename=keyfile)
        stdin, stdout, stderr = ssh_client.exec_command(command)
    except:
        cmdOutput = "Error connecting to hostname "
    try:
        cmdOutput
    except NameError:
        cmdOutput = ""
    if cmdOutput == "":
        while True:
           try:
               cmdOutput += stdout.next()
           except StopIteration:
               break
    try:
        ret_value = stdout.channel.recv_exit_status()
    except:
        ret_value = "unknown"
    with lock:
        print("%s:[%s] \n%s\n" % (cyan(hostname), yellow(ret_value), white(cmdOutput[:-1])))

    ssh_client.close()
    return (hostname, cmdOutput)

def parse_file(filepath):
    file_contents = open(filepath, "r").read()
    file_contents = file_contents.split("\n")
    try:
        file_contents.remove('')
        file_contents.remove('{')
        file_contents.remove('}')
    except:
        pass

    config_pair = dict()

    for i in file_contents:
        line = i.split()
        if (line[0] == "define") or (line[0] == "}"):
            continue
        config_pair[line[0]] = line[1:]

    return config_pair

if __name__ == "__main__":

    all_hosts_info = dict()

    for dirname, dirnames, filenames in os.walk(config['nagios_configs']):
        for filename in filenames:
            all_hosts_info[filename] = parse_file(config['nagios_configs'] + filename)['hostgroups'][0]

    hostgroups_to_hosts = dict()

    for host_info in all_hosts_info.viewitems():
        hostname = host_info[0][:-4]
        hostgroups = host_info[1].split(",")

        for hostgroup in hostgroups:
            if hostgroups_to_hosts.has_key(hostgroup):
                hostgroups_to_hosts[hostgroup] = hostgroups_to_hosts[hostgroup] + " " + hostname
            else:
                hostgroups_to_hosts[hostgroup] = hostname

    host_cmds_list = list()

    for host in hostgroups_to_hosts[sys.argv[1]].split(" "):
        #host_cmds_list.append((host, '/usr/bin/sudo /sbin/service puppet status'))
        host_cmds_list.append((host, sys.argv[2]))

    global lock
    lock = Lock()
    pool = Pool(config['parallel_procs'])

    try:
        pool.map_async(execute_on_host, host_cmds_list).get(9999999)
    except paramiko.SSHException:
        pass
    pool.close()
    pool.join()
