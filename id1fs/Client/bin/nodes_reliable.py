#!/usr/bin/env python3
import subprocess
import time

from helpers import Paths, detect_down_main_nodes, get_file_in_node, remove_created_node_md, get_idfs_status

# run node_reliable.py script while id1fs is on
while get_idfs_status() == "on":
    down_nodes = detect_down_main_nodes()
    for node in down_nodes:
        with open(Paths.get_main_nodes_info(), 'r') as f:
            lines = f.readlines()

        files_names = get_file_in_node(node)
        with open(Paths.get_main_nodes_info(), 'w') as f:
            for line in lines:
                if line.split(" : ")[0] != node:
                    f.write(line)
        remove_created_node_md(node)

        for file in files_names:
            print(file)
            subprocess.run(["restore", file])

    time.sleep(5)
