import sys
import paramiko
from paramiko import SSHClient
import json

CONFIG_FILE = "configure.json"

def journal_paser(source_file, config_dict):
    step_keyword = "Read Configuration"

    try:
        print("journal paser start!")

        user_name = config_dict["user_name"]
        user_pwd = config_dict["user_pwd"]
        host_ip = config_dict["host_ip"]
        remote_path = config_dict["remote_path"]

        local_file = source_file.replace('\\', '/').replace('\"', '')
        local_path = local_file[:local_file.rfind('/')+1]
        local_name = local_file[local_file.rfind('/')+1:]
        remote_name = local_name[:local_name.rfind('.')] + '.txt'
        remote_file = remote_path + remote_name

        print(local_file)
        print(local_path)
        print(local_name)
        print(remote_name)
        print(remote_path)
        print(remote_file)

        step_keyword = "SSH connection"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, 22, user_name, user_pwd)
        print("SSH successfully")

        step_keyword = "SFTP connection"
        tport = paramiko.Transport((host_ip, 22))
        tport.connect(username=user_name, password=user_pwd)
        sftp = paramiko.SFTPClient.from_transport(tport)
        print("SFTP successfully")

        step_keyword = "remove old file"
        stdin, stdout, stderr = ssh.exec_command("rm -f %s/*" %remote_path)
        print(stderr.readlines())

        step_keyword = "upload file"
        sftp.put(local_file, remote_path + local_name)
        print('Upload file successfully')
        print('------')

        step_keyword = "paser journal"
        stdin, stdout, stderr = ssh.exec_command("journalctl -D " + remote_path + " > " + remote_file)
        print(stderr.readlines())

        step_keyword = "download file"
        sftp.get(remote_file, local_path + remote_name)
        print('Download file successfully')
        print('------')

        ssh.close()
        tport.close()

    except Exception:
        print(step_keyword + " error!")

def config_load():
    try:
        root_path = sys.path[0]

        file_desc = open(root_path + "/" + CONFIG_FILE, "r")
        dict_str = json.load(file_desc)
        file_desc.close()
    except Exception:
        dict_str = {}
        print("File open failed!")

    return dict_str

def main():

    if len(sys.argv) != 2:
        print("argv error!")

    source_file = sys.argv[1]
    if not source_file:
        raise MyError("")
    # source_file = "D:/userdata/chrhong/Desktop/system.journal"

    try:
        config_dict = config_load()
        journal_paser(source_file, config_dict)
        raise
    except Exception:
        print("stop to see what error occurs!!!")
        while 1:
            pass

if __name__ == "__main__":
    main()