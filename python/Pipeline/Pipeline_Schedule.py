# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 14:45:41 2022

@author: kient
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:35:31 2022

@author: kient
"""

import os
from PipelineClient import PipelineClient
      
def cmd_copy_file(src_path,dst_path):
    return  'cp ' + src_path + ' ' + dst_path

def cmd_qsub(working_path,pbs_file):
    return  'cd ' + working_path + \
            '; qsub ' + pbs_file
            
def cmd_qstat(username):
    return  'qstat -u ' + username
            
#Get Client
client = PipelineClient()

#Read params
params = client.read_parameters('pipeline.yml')

#Local info
local_upload_dir = params['upload']['local']
local_upload_path = os.path.join(os.getcwd(),local_upload_dir)
   
#Cluster info
cluster_address = params['ssh']['address']
cluster_username = params['ssh']['username']
cluster_key = params['ssh']['key']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)

#Cluster info
cluster_project_dir = params['project']['folder']
cluster_project_path = os.path.join(cluster_home_path,cluster_project_dir)
cluster_target = params['project']['exe']
cluster_target_path = os.path.join(cluster_project_path,cluster_target)
print('Cluster project path: ' + cluster_project_path)
print('Cluster target path: ' + cluster_target_path)

cluster_schedule_dir = params['schedule']['folder']
cluster_schedule_bin = params['schedule']['bin']
cluster_schedule_pbs = params['schedule']['pbs']
cluster_schedule_path = os.path.join(cluster_home_path,cluster_schedule_dir)
cluster_schedule_bin_path = os.path.join(cluster_schedule_path,cluster_schedule_bin)
cluster_schedule_pbs_path = os.path.join(cluster_schedule_path,cluster_schedule_pbs)
cluster_schedule_pbs_file = cluster_schedule_pbs_path.split('/')[-1]
cluster_schedule_pbs_dir = cluster_schedule_pbs_path.replace(cluster_schedule_pbs_file,'')
cluster_schedule_pbs_folder_path = os.path.join(cluster_home_path,cluster_schedule_pbs_dir)
print('Cluster schedule path: ' + cluster_schedule_path)
print('Cluster bin file path: ' + cluster_schedule_bin_path)
print('Cluster pbs file path: ' + cluster_schedule_pbs_path)
print('Cluster pbs folder path: ' + cluster_schedule_pbs_folder_path)
    
#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Copy exe file
client.run_cmd_remotely(cmd_copy_file(cluster_target_path,cluster_schedule_bin_path))
client.print_file_path_exist_remotely(cluster_schedule_bin_path)

#Run schedule command
client.run_cmd_remotely(cmd_qsub(cluster_schedule_pbs_folder_path, cluster_schedule_pbs_file))
client.run_cmd_remotely(cmd_qstat(cluster_username))