Usage:

Make sure you ./objects/hosts/ folder of nagios correctly configured in config.py

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
