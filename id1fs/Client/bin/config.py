#!/usr/bin/env python3
import configparser
import os.path
import sys

from helpers import Paths

config=configparser.ConfigParser()

config["Backups"]={"number": 2}
config["Download"]={"destination" : "/home/ossama/Downloads"}
config["installation"]={"location" : "/home/ossama/Desktop/idfs"}
config["Nodes"]={"max_size" : 100*1024*1024}
with open(os.path.join(sys.path[0],"config.conf"),"w") as configfile:
    config.write(configfile)
config.read("config.conf")
print(config["installation"]["location"])
print(Paths.get_idfs_path())