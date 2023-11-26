import configparser
import json
import logging
import os
import shutil
import subprocess as sbp
import sys
from datetime import datetime
from multiprocessing import Process

import ntplib


class Paths:
    @staticmethod
    def get_idfs_path():
        config = configparser.ConfigParser()
        config.read(os.path.join(sys.path[0],"config.conf"))
        #print(config["Download"]["destination"])
        #print(config.get("installation","location"))
        return config["installation"]["location"]

    @staticmethod
    def get_credentials_path():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/credentials.txt")

    @staticmethod
    def get_log_path():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/actions.log")

    @staticmethod
    def get_connected_path():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/connected_users.txt")

    @staticmethod
    def get_conf_path():
        return os.path.join(Paths.get_idfs_path(), "Client/bin/config.conf")

    @staticmethod
    def get_main_nodes_info():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/main_nodes.txt")

    @staticmethod
    def get_backup_nodes_info():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/backup_nodes.txt")

    @staticmethod
    def get_main_paths_info():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/main_files_path.txt")

    @staticmethod
    def get_backup_paths_info():
        return os.path.join(Paths.get_idfs_path(), "Server/Master/backup_files_path.txt")

    @staticmethod
    def get_best_main_path(file_path=None, filename=None):
        if file_path is not None:
            file_size = os.path.getsize(file_path)
        else:
            file_size = 0

        f = open(Paths.get_main_nodes_info(), "r")
        availables = []
        lines = f.readlines()
        if file_path is None:
            for line in lines:
                if int(line.split(" : ")[1]) > 0 and len(
                        os.listdir(f'{Paths.get_idfs_path()}/Server/Main/{line.split(" : ")[0]}')) != 500:
                    availables.append(line)
        else:
            for line in lines:
                if int(line.split(" : ")[1]) >= file_size:
                    availables.append(line)
        min_node = None
        if len(availables) == 0:
            min_node = create_main_Node()
        else:
            min = 150000000
            for line in availables:
                if int(line.split(" : ")[1]) < int(min):
                    min_node, min = line.split(" : ")

        return f"{Paths.get_idfs_path()}/Server/Main/{min_node}"

    @staticmethod
    def get_best_backup_path(file_path):
        file_size = os.path.getsize(file_path)
        f = open(Paths.get_backup_nodes_info(), "r")
        availables = []
        lines = f.readlines()
        for line in lines:
            if int(line.split(" : ")[1]) >= file_size:
                availables.append(line)

        min_node = None
        if len(availables) == 0:
            min_node = create_backup_Node()
        else:
            min = 150000000
            for line in availables:
                if int(line.split(" : ")[1]) < int(min):
                    min_node, min = line.split(" : ")

        return f"{Paths.get_idfs_path()}/Server/Backup/{min_node}"

    @staticmethod
    def get_files_md_path():
        return os.path.join(Paths.get_idfs_path(), "Server", "Master", "FILES_METADATA")

    @staticmethod
    def get_backups_md_path():
        return os.path.join(Paths.get_idfs_path(), "Server", "Master", "BACKUPS_METADATA")

    @staticmethod
    def get_file_path(filename):
        FILES_METADATA = Paths.get_files_md_path()
        # file_names = os.listdir(FILES_METADATA)

        # Parse file name
        splited_file_name = os.path.splitext(filename)
        file_name = splited_file_name[0]
        ext = splited_file_name[1][1:]

        # read file metadata => extract path
        with open(f"{FILES_METADATA}/{file_name}-md.json") as f:
            file_metadata = json.load(f)
            file_path = f"{Paths.get_idfs_path()}/{'/'.join(file_metadata['Path'].split('/')[-4::])}"

        return file_path

    @staticmethod
    def get_backup_file_path(filename):
        FILES_METADATA = Paths.get_backups_md_path()
        # Parse file name
        splited_file_name = os.path.splitext(filename)
        file_name = splited_file_name[0]
        ext = splited_file_name[1][1:]

        # read file metadata => extract path
        with open(f"{FILES_METADATA}/{file_name}-md.json") as f:
            file_metadata = json.load(f)
            backup_path = f"{Paths.get_idfs_path()}/{'/'.join(file_metadata['Path'].split('/')[-4::])}"
        return backup_path

    @staticmethod
    def get_nodes_md():
        return f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json"

    @staticmethod
    def get_idfs_status_path():
        return f"{Paths.get_idfs_path()}/Server/Master/idfs_status.json"


def get_connected_user():
    # return the connected user from id1fs json status file 
    with open(Paths.get_idfs_status_path(), "r") as f:
        data = json.load(f)
    return data["connected user"]


def set_connected_user(name):
    # set the connected user into id1fs json status file 
    with open(Paths.get_idfs_status_path(), "r") as f:
        data = json.load(f)
    data["connected user"] = name

    # update id1fs json status file
    with open(Paths.get_idfs_status_path(), "w") as f:
        json.dump(data, f, indent=4)


# Logger configuration
def logger_config():
    if get_connected_user() != None:
        connected = get_connected_user()
    else:
        connected = "system"
    logging.basicConfig(filename=Paths.get_log_path(),
                        level=logging.DEBUG,
                        format=f'%(levelname)s : {connected} : %(asctime)s : %(message)s')


logger_config()


# create file in data section
def create_file(filename):
    main_path = os.path.join(Paths.get_idfs_path(), f"Server/Main/ji/{filename}")
    # check if name already used
    if os.path.exists(main_path):
        print("The file is already existing ,retry with another name")
        logging.error(f"Failed to create < {filename} > --> The file already existing")
        return False
    else:
        # create new file
        node_path = Paths.get_best_main_path()
        open(f"{node_path}/{filename}", "w").close()
        create_file_md(filename, node_path)
        print(f"The file < {filename} > created successfully")
        logging.info(f"The file < {filename} > created successfully")
        return True


# to create the file in Backup section
def backup_file(file_path):
    main_path = file_path
    node_path = Paths.get_best_backup_path(file_path)
    backup_path = os.path.join(node_path, os.path.basename(file_path))
    shutil.copy(main_path, backup_path)
    create_backup_md(os.path.basename(file_path), node_path)
    handle_backup_add_node_size(backup_path)
    print(f"The file < {os.path.basename(file_path)} > successfully backed up")
    logging.info(f"The file < {os.path.basename(file_path)} > successfully backed up")


# to delete the file from main section
def delete_file(filename):
    # check if file exists
    if not check_main_file_exist(filename):
        print("File does not exist in Main Section .")
        logging.error(f"Failed to delete < {filename} > --> File does not exist in Main Section ")
        return
    node_name = Paths.get_file_path(filename).split("/")[-2]
    main_path = os.path.join(Paths.get_idfs_path(), f"Server/Main/{node_name}/{filename}")

    # delete file and his dependicies (from fsimage, backup, metadata)
    if os.path.exists(main_path):
        handle_main_remove_node_size(main_path)
        os.remove(main_path)
        print(f"The file {filename} removed from main section successfully")
        logging.info(f"The file < {filename} > removed successfully from main section")
        # remove file metadata
        delete_file_md(filename)
        remove_created_file_image_md(filename, node_name)

        if len(os.listdir(os.path.join(Paths.get_idfs_path(), f"Server/Main/{node_name}"))) == 0:
            remove_created_node_md(node_name)
            os.rmdir(os.path.join(Paths.get_idfs_path(), f"Server/Main/{node_name}"))
            with open(Paths.get_main_nodes_info(), 'r') as f:
                lines = f.readlines()

            with open(Paths.get_main_nodes_info(), 'w') as f:
                for line in lines:
                    if line.split(" : ")[0] != node_name:
                        f.write(line)


    else:
        print(f"The file {filename} not found in main section")
        logging.error(f"Failed to delete < {filename} > --> File not found in main section")


# create main node
def create_main_Node():
    node_name = choose_main_node_name()
    Node_path = os.path.join(Paths.get_idfs_path(), "Server", "Main", node_name)
    os.makedirs(Node_path, exist_ok=True)
    f = open(Paths.get_main_nodes_info(), "a")
    f.writelines(f"{node_name} : 500\n")
    f.close()
    add_created_node_md(node_name)
    return node_name

# create backup node
def create_backup_Node():
    node_name = choose_backup_node_name()
    Node_path = os.path.join(Paths.get_idfs_path(), "Server", "Backup", node_name)
    os.makedirs(Node_path, exist_ok=True)
    f = open(Paths.get_backup_nodes_info(), "a")
    f.writelines(f"{node_name} : 500\n")
    f.close()
    return node_name


# to delete the file from backup section
def delete_backup(filename):
    # backup_path = os.path.join(Paths.get_idfs_path(),"Server","Backup","Node1",filename)
    backup_path = Paths.get_backup_file_path(filename)
    node_name = backup_path.split("/")[-2]
    if os.path.exists(backup_path):
        handle_backup_remove_node_size(backup_path)
        os.remove(backup_path)
        print(f"The file {filename} removed from backup section successfully")
        logging.info(f"The file < {filename} > removed from backup section successfully")
        # remove backup file metadata
        delete_backup_file_md(filename)

        if len(os.listdir(os.path.join(Paths.get_idfs_path(), f"Server/Backup/{node_name}"))) == 0:
            os.rmdir(os.path.join(Paths.get_idfs_path(), f"Server/Backup/{node_name}"))
            with open(Paths.get_backup_nodes_info(), 'r') as f:
                lines = f.readlines()

            with open(Paths.get_backup_nodes_info(), 'w') as f:
                for line in lines:
                    if line.split(" : ")[0] != node_name:
                        f.write(line)
    else:
        print(f"The file {filename} not found in backup")
        logging.error(f"Failed to delete < {filename} > --> File not found in backup section")


# choose main node name
def choose_main_node_name():
    f = open(Paths.get_main_nodes_info(), 'r')
    if len(f.readlines()) == 0:
        f.close()
        return "Node1"
    f = open(Paths.get_main_nodes_info(), 'r')
    last_node = f.readlines()[-1].split(" : ")[0]
    last_node_number = int(last_node[4:])
    f.close()
    return f"Node{last_node_number + 1}"


# choose backup node name
def choose_backup_node_name():
    f = open(Paths.get_backup_nodes_info(), 'r')
    if len(f.readlines()) == 0:
        f.close()
        return "Node1"
    f = open(Paths.get_backup_nodes_info(), 'r')
    last_node = f.readlines()[-1].split(" : ")[0]
    last_node_number = int(last_node[4:])
    f.close()
    return f"Node{last_node_number + 1}"


# return the list of used arguments with option to select those with certain value
def list_from_args(args, value=None):
    l = []
    for k, v in dict(args.__dict__).items():
        if value != None:
            if v != value:
                continue
        l.append(k)
    return l


# return a list of used args keys
def used_args(args):
    l = []
    for k, v in dict(args.__dict__).items():
        if v == True:
            l.append(k)
    return l


# synchronize nodes info in main_nodes.txt after 'file addition'
def handle_main_add_node_size(file_path):
    file_size = os.path.getsize(file_path)
    node_name = file_path.split("/")[-2]
    f = open(Paths.get_main_nodes_info(), "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith(node_name + " "):
            prev_size = int(line.split(" : ")[1])
            new_size = prev_size - file_size
            lines[i] = f"{node_name} : {new_size}\n"
            break
    f.close()
    f = open(Paths.get_main_nodes_info(), "w")
    f.write("".join(lines))
    f.close()


# synchronize nodes info in backup_nodes.txt after file 'addition'
def handle_backup_add_node_size(file_path):
    file_size = os.path.getsize(file_path)
    node_name = file_path.split("/")[-2]
    f = open(Paths.get_backup_nodes_info(), "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith(node_name + " "):
            prev_size = int(line.split(" : ")[1])
            new_size = prev_size - file_size
            lines[i] = f"{node_name} : {new_size}\n"
            break
    f.close()
    f = open(Paths.get_backup_nodes_info(), "w")
    f.write("".join(lines))
    f.close()

# synchronize nodes info in main_nodes.txt after file 'deletion'
def handle_main_remove_node_size(file_path):
    file_size = os.path.getsize(file_path)
    node_name = file_path.split("/")[-2]
    f = open(Paths.get_main_nodes_info(), "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith(node_name + " "):
            prev_size = int(line.split(" : ")[1])
            new_size = prev_size + file_size
            lines[i] = f"{node_name} : {new_size}\n"
            break
    f.close()
    q = open(Paths.get_main_nodes_info(), "w")
    q.write("".join(lines))
    q.close()

# synchronize nodes info in backup_nodes.txt after file 'deletion'
def handle_backup_remove_node_size(file_path):
    file_size = os.path.getsize(file_path)
    node_name = file_path.split("/")[-2]
    f = open(Paths.get_backup_nodes_info(), "r")
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith(node_name + " "):
            prev_size = int(line.split(" : ")[1])
            new_size = prev_size + file_size
            lines[i] = f"{node_name} : {new_size}\n"
            break
    f.close()
    q = open(Paths.get_backup_nodes_info(), "w")
    q.write("".join(lines))
    q.close()


# store file metadata in a json file for each file creation
def create_file_md(filename, node_path):
    splited_file_name = os.path.splitext(filename)
    file_name = splited_file_name[0]
    ext = splited_file_name[1][1:]

    # store the output of exiftool in a file
    with open("bridge", 'w') as f:
        sbp.run(["exiftool", f"{node_path}/{filename}"], stdout=f, text=True)

    file_metadata = {}
    with open("bridge") as f:
        for line in f:
            key, value = line.split(" : ")
            file_metadata[key.strip()] = value[:-1]
    file_metadata["Path"] = f"{node_path}/{filename}"
    file_metadata["Owner"] = get_connected_user()

    # create json file for metadata
    with open(f"{Paths.get_files_md_path()}/{file_name}-md.json", 'w') as js_file:
        json.dump(file_metadata, js_file, indent=4)

    add_created_file_md(filename, os.path.basename(node_path))
    # delete bridge
    os.remove("bridge")


# store file backup! metadata in a json file for each file creation
def create_backup_md(filename, node_path):
    splited_file_name = os.path.splitext(filename)
    file_name = splited_file_name[0]
    ext = splited_file_name[1][1:]

    # store the output of exiftool in a file
    with open("bridge", 'w') as f:
        sbp.run(["exiftool", f"{node_path}/{filename}"], stdout=f, text=True)

    file_metadata = {}
    with open("bridge") as f:
        for line in f:
            # print(line)
            key, value = line.split(" : ")
            file_metadata[key.strip()] = value[:-1]
        file_metadata["Path"] = f"{node_path}/{filename}"

    # create json file for metadata
    with open(f"{Paths.get_backups_md_path()}/{file_name}-md.json", 'w') as js_file:
        json.dump(file_metadata, js_file, indent=4)
    # delete bridge
    os.remove("bridge")


# delete file metadata after file deletion
def delete_file_md(filename):
    FILES_METADATA = Paths.get_files_md_path()
    file_names = os.listdir(FILES_METADATA)

    # Parse file name
    splited_file_name = os.path.splitext(filename)
    file_name = splited_file_name[0]
    ext = splited_file_name[1][1:]

    # delete json file
    os.remove(f"{FILES_METADATA}/{file_name}-md.json")


# delete file backup metadata after file deletion
def delete_backup_file_md(filename):
    FILES_METADATA = Paths.get_backups_md_path()
    file_names = os.listdir(FILES_METADATA)

    # Parse file name
    splited_file_name = os.path.splitext(filename)
    file_name = splited_file_name[0]
    ext = splited_file_name[1][1:]

    # delete json file
    os.remove(f"{FILES_METADATA}/{file_name}-md.json")


# check if the file exist the main node
def check_main_file_exist(file_name):
    Main_folder = os.path.join(Paths.get_idfs_path(), "Server", "Main")
    file_names = []
    for Node in os.listdir(Main_folder):
        for file in os.listdir(f"{Main_folder}/{Node}"):
            file_names.append(file)

    if file_name in file_names:
        return True
    else:
        return False

# check if file exist in the backup
def check_backup_file_exist(file_name):
    FILES_METADATA = Paths.get_backups_md_path()
    file_names = os.listdir(FILES_METADATA)
    if f"{os.path.splitext(file_name)[0]}-md.json" in file_names:
        return True
    else:
        return False


# restore file from backup
def restore(file_backup_path):
    main_path = os.path.join(Paths.get_best_main_path(file_backup_path), os.path.basename(file_backup_path))
    shutil.copy(file_backup_path, main_path)
    create_file_md(os.path.basename(main_path), os.path.dirname(main_path))
    handle_main_add_node_size(main_path)
    print(f"The file {os.path.basename(file_backup_path)} restored from backup section successfully")
    logging.info(f"The file < {os.path.basename(file_backup_path)} > restored from backup section successfully")


# add node to id1fs metadata
def add_created_node_md(node_name):
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    data["Nodes"][node_name] = []
    with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'w') as f:
        json.dump(data, f, indent=4)


# add file to id1fs metadata
def add_created_file_md(file_name, node_name):
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    if file_name not in data["Nodes"][node_name]:
        data["Nodes"][node_name].append(file_name)
    with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'w') as f:
        json.dump(data, f, indent=4)


# remove file name from id1fs fsimage(nodes_md.json)
def remove_created_file_image_md(file_name, node_name):
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    data["Nodes"][node_name].remove(file_name)
    with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'w') as f:
        json.dump(data, f, indent=4)


# remove node name from id1fs fsimage(nodes_md.json)
def remove_created_node_md(node_name):
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    del data["Nodes"][node_name]
    with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'w') as f:
        json.dump(data, f, indent=4)


# return the status of id1fs
def get_idfs_status():
    with open(Paths.get_idfs_status_path(), 'r') as f:
        data = json.load(f)

    return data['status']


# filter connected user files by extension
def filter_by_extension(md_folder_location_path, ext):
    # get metadata folder location
    md_file_path = os.listdir(md_folder_location_path)
    desired_ext = ext.lower()
    counter = 0
    for file in md_file_path:
        with open(f'{md_folder_location_path}/{file}') as json_file:
            file_md = json.load(json_file)
            # get file extension
            splited_name = os.path.splitext(file_md['File Name'])
            ext = splited_name[1][1:]

            # ensure the extension and if connected user is also the owner
            if ext == desired_ext and get_connected_user() == file_md["Owner"]:
                print(file_md['File Name'])
                counter += 1
    # print the founded files and log info
    if counter <= 1:
        print(f"{counter} file found")
    else:
        print(f"{counter} files found")
    logging.info("Filtered by extention successfully")


# filter connected user files by size interval [min, max]
def filter_by_size(md_folder_location_path, min, max):
    # get metadata folder location
    md_file_path = os.listdir(md_folder_location_path)
    interval = [min, max]
    counter = 0
    for file in md_file_path:
        with open(f'{md_folder_location_path}/{file}') as json_file:
            file_md = json.load(json_file)
            splited_path_name = os.path.split(file_md['File Size'])
            size0 = splited_path_name[1]
            size1 = size0.split(' ')
            size = int(size1[0])

            # ensure file size and if the connected user is also the owner
            if interval[0] <= size <= interval[1] and get_connected_user() == file_md["Owner"]:
                print("File Name: ", file_md['File Name'], end=' : ')
                print(size, 'bytes')
                counter += 1
    # print the founded files and log info
    if counter <= 1:
        print(f"{counter} file found")
    else:
        print(f"{counter} files found")
    logging.info("Filtered by extention successfully")


# check if any node is done
def detect_down_main_nodes():
    with open(f"{Paths.get_idfs_path()}/Server/Master/nodes_md.json", 'r') as f:
        nodes = json.load(f)
        down_main_nodes = []
        existing_nodes = os.listdir(f"{Paths.get_idfs_path()}/Server/Main")
        for node in nodes['Nodes']:
            if node not in existing_nodes:
                down_main_nodes.append(node)

    return down_main_nodes


# return a list of a node file names
def get_file_in_node(node_name):
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    files_names = data["Nodes"][node_name]
    return files_names


# return a list of server nodes
def get_nodes():
    with open(Paths.get_nodes_md(), 'r') as f:
        data = json.load(f)

    nodes_names = list(data["Nodes"].keys())
    return nodes_names


# disconnect user by setting connected user field to "system"
def disconnect():
    connected_user = get_connected_user()
    print(f"The user < {connected_user} > is disconnected successfully")
    logging.info(f"The user < {connected_user} > is disconnected successfully")
    set_connected_user("system")


# return a python object (dict) of file metadata
def get_file_md(file_name):
    with open(f"{Paths.get_idfs_path()}/Server/Master/FILES_METADATA/{os.path.splitext(file_name)[0]}-md.json") as f:
        data = json.load(f)

    return data


# turn-on id1fs by setting status to "on"
def turn_on():
    with open(Paths.get_idfs_status_path(), 'r') as f:
        data = json.load(f)

    data["status"] = "on"

    with open(Paths.get_idfs_status_path(), 'w') as f:
        json.dump(data, f, indent=4)

    logging.info("ID1FS is turned on successfully")


# turn-off id1fs by setting status to "off"
def turn_off():
    with open(Paths.get_idfs_status_path(), 'r') as f:
        data = json.load(f)

    data["status"] = "off"

    with open(Paths.get_idfs_status_path(), 'w') as f:
        json.dump(data, f, indent=4)


def nodes_reliable():
    # run nodes_reliable script in the background
    p = sbp.Popen(["nohup", "nodes_reliable.py", "&"], stdout=sbp.DEVNULL, stderr=sbp.DEVNULL)


def time_check():
    # run ntptime script in the background
    sbp.Popen(["nohup", "ntptime.py", "&"], stdout=sbp.DEVNULL, stderr=sbp.DEVNULL)


def backup_master():
    # run master_backup script in the background
    sbp.Popen(["nohup", "master_backup.py", "&"], stdout=sbp.DEVNULL, stderr=sbp.DEVNULL)


def run_bg_script():
    # run 3 scripts in the background
    a = Process(target=nodes_reliable)
    b = Process(target=time_check)
    c = Process(target=backup_master)

    a.start()
    b.start()
    c.start()

    a.join()
    b.join()
    c.join()


# exit if id1fs is off
def exit_if_off():
    if get_idfs_status() == "off":
        print("You can not use this command. Please 'turn on' ID1FS first.")
        logging.error("You can not use this command. Please 'turn on' ID1FS first.")
        sys.exit()


# exit if no user is connected
def exit_if_disconnected():
    if get_connected_user() == "system":
        print("Can not use this command. Please 'connect' to ID1FS first ")
        logging.error("Can not use this command. Please 'connect' to ID1FS first ")
        sys.exit()


# set time to "configured"
def set_time_configured():
    with open(Paths.get_idfs_status_path(), "r") as f:
        data = json.load(f)

    data["time"] = "configured"

    with open(Paths.get_idfs_status_path(), "w") as f:
        json.dump(data, f, indent=4)


# set time to "not configured"
def set_time_not_configured():
    with open(Paths.get_idfs_status_path(), "r") as f:
        data = json.load(f)

    data["time"] = "not configured"

    with open(Paths.get_idfs_status_path(), "w") as f:
        json.dump(data, f, indent=4)


# return id1fs time status [configured->true, else->false]
def is_time_configured():
    with open(Paths.get_idfs_status_path(), "r") as f:
        data = json.load(f)

    if data["time"] == "configured":
        return True
    else:
        return False


# exit if user machine time is not configured
def exit_if_not_configured():
    if not is_time_configured():
        print("Please configure time ,and try again")
        disconnect()
        sys.exit()


# check uf user machine time is synchronized or no
def check_time_sync():
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request("pool.ntp.org")
        timestamp = response.tx_time

        # get international time and user machine time
        reference_datetime = datetime.fromtimestamp(timestamp)
        user_datetime = datetime.now()

        # check if time is synchronized
        time_difference = abs(user_datetime - reference_datetime)
        threshold = 40
        if not time_difference.seconds < threshold:
            logging.error("Time configuration is required to use ID1FS")
            set_time_not_configured()
            turn_off()
            set_connected_user("system")
            return False
        else:
            set_time_configured()
            return True
    except Exception as e:
        set_time_configured()
        return True


def read_md(filename):
    # split file name to format metadata file name
    splited_name = os.path.splitext(filename)
    clean_name = splited_name[0]

    # delete fields which are unnecessary for the user
    with open(f"{Paths.get_files_md_path()}/{clean_name}-md.json") as f:
        file_md = json.load(f)
    del file_md['ExifTool Version Number']
    del file_md['Directory']
    del file_md['Path']
    del file_md['File Permissions']
    if 'Error' in file_md.keys():
        del file_md['Error']

    return file_md


# allow connected user to add metadata to his files
def add_md(filename, key):
    # define forbiden to change metadata
    forbiden_keys = ["File Name", "File Size", "File Modification Date/Time", "File Access Date/Time",
                     "File Inode Change Date/Time", "File Type", "File Type Extension"]
    splited_name = os.path.splitext(filename)
    clean_name = splited_name[0]

    # get file metadata and add field
    with open(f"{Paths.get_files_md_path()}/{clean_name}-md.json") as f:
        file_md = json.load(f)

    if "Added keys" not in file_md:
        file_md["Added keys"] = []

    if key not in forbiden_keys:
        value = input(f"['{key}'] = ?\n")
        file_md["Added keys"].append(key)
        file_md[key] = value
    else:
        print(f"You can not modify this metadata : {key}")
        logging.error(f"Failed to modify metadata --> {key} is a sensitive metadata")
        sys.exit()

    with open(f"{Paths.get_files_md_path()}/{clean_name}-md.json", 'w') as f:
        json.dump(file_md, f, indent=4)

    with open(f"{Paths.get_backups_md_path()}/{clean_name}-md.json") as f:
        file_md = json.load(f)

    if "Added keys" not in file_md:
        file_md["Added keys"] = []

    file_md[key] = value

    with open(f"{Paths.get_backups_md_path()}/{clean_name}-md.json", 'w') as f:
        json.dump(file_md, f, indent=4)


# get default download destination
def get_download_destination():
    config = configparser.ConfigParser()
    config.read(os.path.join(sys.path[0], "config.conf"))
    return config["Download"]["destination"]


# exit if user didn't set yet the download destination
def exit_if_download_not_set():
    if get_download_destination() == "Not set" :
        print("Please set your download destination in the config.conf file before downloading.")
        logging.error("Failed to download --> Please set your download destination in the config.conf file before downloading")
        sys.exit()
