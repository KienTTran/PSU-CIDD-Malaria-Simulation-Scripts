# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

import paramiko
import os
from stat import S_ISDIR, S_ISREG
    
def sftp_download_recursive(sftp, remotepath, localpath):
    # if fileattr.filename.startswith('Temat') and fileattr.st_mtime > latest:
    #     latest = fileattr.st_mtime
    #     latestfile = fileattr.filename
    if not os.path.isdir(localpath):
        os.makedirs(localpath, exist_ok=True)           
    for item in sftp.listdir_attr(remotepath):
        mode = item.st_mode
        if S_ISDIR(mode):
            sftp_download_recursive(sftp,remotepath + "/" + item.filename, localpath + "/" + item.filename)
        elif S_ISREG(mode):
            sftp.get(remotepath + "/" + item.filename, localpath + "/" + item.filename)
            print("#",end="")
            
def download_simulations(sftp, remotepath, localpath, simulation_keywords): 
    for item in sftp.listdir_attr(remotepath):
        mode = item.st_mode
        if S_ISDIR(mode):
            if any(x in item.filename for x in simulation_keywords):
                print("Downloading directory " + item.filename)
                print("[",end="")
                sftp_download_recursive(sftp, remotepath + "/" + item.filename, localpath + "/" + item.filename)
                print("]")
                
def connect_to_cluster(ssh_client,host,port,username,password,totp):    
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    for i in range(3):
        try:
            ssh_client.totp = totp
            ssh_client.duo_auth = True
            ssh_client.connect(host, port=port, username=username, password=password)
            break
        except paramiko.AuthenticationException:
            print("Authentication didn't work! Retry")      
    sftp = ssh_client.open_sftp() 
    return sftp
