from os import environ as getenv

config = {
    'username' : "abhijeet.ras",
    'keyname' : "id_rsa_directi",
    'nagios_configs' : "./objects/hosts/",
    'parallel_procs' : 100,
}

config['keyfile'] = getenv['HOME'] + "/.ssh/" + config['keyname']
