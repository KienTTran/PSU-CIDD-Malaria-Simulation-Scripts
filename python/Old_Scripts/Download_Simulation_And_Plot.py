# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

import paramiko
import os
import time
from stat import S_ISDIR, S_ISREG
from glob import glob
from Function_Plot_All_Data_Debug_Population_Genotypes_Daily import plot_rep_from_file
from SSH_Client import SSHClient

host = "datamgr.aci.ics.psu.edu"
port = 22
username = ""
password = ""
totp = ""
remotepath = "/storage/home/k/" + username + "/Simulations/"
simulation_keywords = [
            "PRMC_Kien_Parasite_Id_10K",
            ]
plot_keywords = [
            "Daily_PG",
            # "Daily_PRMC",
            # "Single_",
            # "_4000_",
            "_0.19_0.15",
            # "_2037_",
            # "_2537_",
            ]
localpath = "D:/plot/Simulations"

def sftp_get_recursive(remotepath, localpath, sftp):
    if not os.path.isdir(localpath):
        os.makedirs(localpath, exist_ok=True)   
        
    for item in sftp.listdir_attr(remotepath):
        mode = item.st_mode
        if S_ISDIR(mode):
            sftp_get_recursive(remotepath + "/" + item.filename, localpath + "/" + item.filename, sftp)
        elif S_ISREG(mode):
            sftp.get(remotepath + "/" + item.filename, localpath + "/" + item.filename)
            
def sftp_get_simulations(remotepath, localpath, sftp, keywords):        
    for item in sftp.listdir_attr(remotepath):
        mode = item.st_mode
        if S_ISDIR(mode):
            if all(x in item.filename for x in simulation_keywords):
                sftp_get_recursive(remotepath + "/" + item.filename, localpath + "/" + item.filename, sftp)

def sftp_download_simulations():    
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while True:
        for i in range(3):
            try:
                ssh.totp = totp
                ssh.duo_auth = True
                ssh.connect(host, port=port, username=username, password=password)
                break
            except paramiko.AuthenticationException:
                print("Authentication didn't work! Retry")
        sftp = ssh.open_sftp()
        #Download
        sftp_get_simulations(remotepath,localpath,sftp,simulation_keywords) 
        #Read folders
        rep_files = []  
        for root, folders, files in os.walk(localpath, topdown=False):
            for file in files:
                if file.endswith(".txt") and all(x in file for x in plot_keywords):
                    rep_files.append(os.path.join(root, file))
        #Plot
        for rep_file in rep_files:
            plot_rep_from_file(rep_file,2)
    
        time.sleep(10)


