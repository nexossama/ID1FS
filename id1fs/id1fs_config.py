import configparser
import json
import os
import sys
import shutil
import time
import subprocess

#format the ID1FS by deleting all existing files completely
def format_id1fs():
      format = input("\nDo you want to format your ID1FS ? \n"
                     "Note that format will delete all available files permanently!! [y/n] : ")

      if format.upper()!="Y":
            print("\nID1FS is not formated")
            return
      # delete all main nodes
      Main_PATH = f"{sys.path[0]}/Server/Main"
      for dirname in os.listdir(Main_PATH):
            file_path = os.path.join(Main_PATH, dirname)
            shutil.rmtree(file_path)

      #delete all backup nodes
      Backup_PATH = f"{sys.path[0]}/Server/Backup"
      for dirname in os.listdir(Backup_PATH):
            file_path = os.path.join(Backup_PATH, dirname)
            shutil.rmtree(file_path)

      #delete metadata of all files in main section
      Files_METADATA_PATH = os.path.join(sys.path[0], "Server", "Master", "FILES_METADATA")
      for filename in os.listdir(Files_METADATA_PATH):
            file_path = os.path.join(Files_METADATA_PATH, filename)
            os.unlink(file_path)

      #delete metadata of all files in backup section
      Backups_METADATA_PATH = os.path.join(sys.path[0], "Server", "Master", "BACKUPS_METADATA")
      for filename in os.listdir(Backups_METADATA_PATH):
            file_path = os.path.join(Backups_METADATA_PATH, filename)
            os.unlink(file_path)

      #delete logs
      actions_log_PATH = os.path.join(sys.path[0], "Server", "Master", "actions.log")
      f = open(actions_log_PATH, 'w').close()

      #delete main nodes metadata
      main_nodes_md_PATH = os.path.join(sys.path[0], "Server", "Master", "main_nodes.txt")
      f = open(main_nodes_md_PATH, 'w').close()
      with open(os.path.join(sys.path[0], "Server", "Master", "nodes_md.json")) as f:
            data = json.load(f)
      data["Nodes"] = {}
      with open(os.path.join(sys.path[0], "Server", "Master", "nodes_md.json"), "w") as f:
             json.dump(data, f, indent=4)

      #delete backup nodes metadata
      backup_nodes_md_PATH = os.path.join(sys.path[0], "Server", "Master", "backup_nodes.txt")
      f = open(backup_nodes_md_PATH, 'w').close()

      #remove all created users
      credentials_PATH = os.path.join(sys.path[0], "Server", "Master", "credentials.txt")
      f = open(credentials_PATH, 'w').close()

      #reset ID1FS to initial status
      with open(os.path.join(sys.path[0], "Server", "Master", "idfs_status.json")) as f:
            data = json.load(f)
      data["status"] = "off"
      data["connected user"] = "system"
      data["time"] = "not configured"
      with open(os.path.join(sys.path[0], "Server", "Master", "idfs_status.json"), "w") as f:
            json.dump(data, f, indent=4)

      config = configparser.ConfigParser()
      config.read(os.path.join(sys.path[0], "Client", "bin", "config.conf"))


      config.set("Download", "destination", "not set")
      with open(os.path.join(sys.path[0], "Client", "bin", "config.conf"), "w") as configfile:
            config.write(configfile)


      print("\n--> ID1FS is formated succesfully")

#set the default download destination
def set_download_location():
      config = configparser.ConfigParser()
      config.read(os.path.join(sys.path[0], "Client", "bin", "config.conf"))

      location = input("\nPlease set a default download location : ")
      while not os.path.exists(location):
            location = input("Please set a valid download location : ")

      config.set("Download", "destination", location)
      with open(os.path.join(sys.path[0], "Client", "bin", "config.conf"), "w") as configfile:
            config.write(configfile)

      print("\n--> Download destination is set up succesfully")
      time.sleep(1)
      print("\n--> Notice : \n"
            "You can change this download location anytime by accesing : \n    id1fs/Client/bin/config.conf \n"
            "Or simply by using the < id1fs_config.py > tool.")
      time.sleep(1)

#set the idfs installation path
def set_installation():
      config = configparser.ConfigParser()
      config.read(os.path.join(sys.path[0], "Client", "bin", "config.conf"))
      print("\n--> ID1FS location is set up succesfully")
      config.set("installation","location",sys.path[0])
      with open(os.path.join(sys.path[0], "Client", "bin", "config.conf"), "w") as configfile:
            config.write(configfile)
      subprocess.run(["chmod", "-R", "+x", f"{sys.path[0]}/Client/bin"])


print("\n",
      "-----------------------------------\n",
      "██╗██████╗░░░███╗░░███████╗░██████╗\n",
      "██║██╔══██╗░████║░░██╔════╝██╔════╝\n",
      "██║██║░░██║██╔██║░░█████╗░░╚█████╗░\n",
      "██║██║░░██║╚═╝██║░░██╔══╝░░░╚═══██╗\n",
      "██║██████╔╝███████╗██║░░░░░██████╔╝\n",
      "╚═╝╚═════╝░╚══════╝╚═╝░░░░░╚═════╝░\n",
      "-----------------------------------\n",
              )

#handling options
option=-1
while option != 0 :
      print("\n--------Configuration utlity-------\n")
      print("1 : Set ID1FS location ")
      print("2 : Set default download destination")
      print("3 : Format ID1FS")
      print("4 : All")
      print("0 : Quit ID1FS configuration utility ")

      try:
            option = int(input("\nPlease choose an option : "))
      except:
            print("\nPlease choose a valid option")
            continue

      if option==1:
            set_installation()
      elif option==2:
            set_download_location()
      elif option==3:
            format_id1fs()
      elif option==4:
            set_installation()
            set_download_location()
            format_id1fs()
      elif option==0:
            break
      else:
            print("\nPlease choose a valid option")

      time.sleep(2)


print("\nThanks for using ID1FS configuration utility.")
time.sleep(1)
print("\nThe ID1FS configuration utility will quit within 3 seconds")
time.sleep(3)