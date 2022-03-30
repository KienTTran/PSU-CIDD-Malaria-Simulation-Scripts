# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

import time
import paramiko
import select
from Download_Simulations import download_simulations,connect_to_cluster
from Read_Simulations import read_simulations
from Plot_Simulations import plot_simulations
from SSH_Client import SSHClient

host = "datamgr.aci.ics.psu.edu"
port = 22
username = "ktt5121"
password = ""
totp = "123456"
remote_path = "/storage/home/k/" + username + "/Simulations/"
simulation_keywords = [
            "PRMC_Kien_Parasite_Id_10K",
            "PRMC_Kien_Parasite_Id2_10K",
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
local_path = "D:/plot/Simulations/"
plot_delay = 2
download_delay = 300

def main():   
    ssh_client = SSHClient()
    sftp = connect_to_cluster(ssh_client, host, port, username, password, totp) 
    
    download_simulations(sftp,remote_path,local_path,simulation_keywords)     
    simulations = read_simulations(local_path, plot_keywords, plot_delay)
    plot_simulations(simulations, plot_delay) 
    
    # while True:    
    #     download_simulations(sftp,remote_path,local_path,simulation_keywords) 
    #     time.sleep(5)
    #     simulations = read_simulations(local_path, plot_keywords, plot_delay)
    #     plot_simulations(simulations, plot_delay)
    #     time.sleep(download_delay)

if __name__ == "__main__":
    main()
