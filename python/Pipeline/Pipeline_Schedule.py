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
      
def cmd_generate(working_path,generate_script,parameters):
    return  'cd ' + working_path + \
            '; python3 ' + generate_script + ' ' + parameters
            
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
    
#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check exe file





