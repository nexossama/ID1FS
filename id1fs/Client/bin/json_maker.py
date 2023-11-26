#!/usr/bin/env python3

import json
from helpers import Paths

# built id1fs file image
dic = {
    "Nodes":
        {
            "Node1": []
        }
}

with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'w') as f:
    json.dump(dic, f, indent=4)
