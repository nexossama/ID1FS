#!/usr/bin/env python3

import os
import shutil
import time
import json
from helpers import Paths, get_idfs_status

master_path = f"{Paths.get_idfs_path()}/Server/Master"
backup_master_path = f"{Paths.get_idfs_path()}/Server/Backup_Master"


def get_current_idfs_status():
    if os.path.exists(master_path):
        with open(Paths.get_idfs_status_path(), 'r') as f:
            data = json.load(f)

        return data['status']

    else:
        with open(f"{Paths.get_idfs_path()}/Server/Backup_Master/idfs_status.json", 'r') as f:
            data = json.load(f)

        return data['status']


while get_current_idfs_status() == "on":
    if os.path.exists(master_path):
        os.makedirs(backup_master_path, exist_ok=True)
        shutil.copytree(master_path, backup_master_path, dirs_exist_ok=True)

    else:
        os.makedirs(master_path, exist_ok=True)
        shutil.copytree(backup_master_path, master_path, dirs_exist_ok=True)

    time.sleep(3)
