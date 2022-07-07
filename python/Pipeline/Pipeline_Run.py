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
from SSHClient import SSHClient
      
def cmd_generate_configs(generate_path):
    return 'soon'
    
#Get Client
client = SSHClient()

#Read params
params = client.read_parameters('pipeline.yml')
   
#Cluster info
cluster_address = params['cluster']['address']
cluster_username = params['cluster']['username']
cluster_key = params['cluster']['key']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)

#Run info
build_workplace_dir = params['build']['workplace_dir']
build_project_dir = params['build']['project_dir']
cluster_build_workplace_path = os.path.join(cluster_home_path,build_workplace_dir)
cluster_build_path = os.path.join(os.path.join(cluster_build_workplace_path,build_project_dir),'build/bin')
run_workplace_dir = params['run']['workplace_dir']
run_project_dir = params['run']['project_dir']
run_local_dir = params['run']['local_dir']
run_generate_file = params['run']['generate_file']
run_parameter_file = params['run']['parameter_file']
run_config_file = params['run']['config_file']
run_job_template_file = params['run']['job_template_file']
run_submit_job_template_file = params['run']['submit_job_template_file']
run_exe = params['run']['exe']
cluster_exe_path = os.path.join(cluster_build_path,run_exe)
cluster_run_workplace_path = os.path.join(cluster_home_path,run_workplace_dir)
cluster_run_project_path = os.path.join(cluster_run_workplace_path,run_project_dir)
print('Build workplace path: ' + cluster_build_workplace_path)
print('Build project path: ' + cluster_build_path)
print('Run workplace path: ' + cluster_run_workplace_path)
print('Run project build path: ' + cluster_run_project_path)
print('Run exe path: ' + cluster_exe_path)
 
local_generate_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_generate_file)
local_parameter_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_parameter_file)
local_config_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_config_file)
local_job_template_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_job_template_file)
local_submit_job_template_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_submit_job_template_file)
print('Local generate path: ' + local_generate_path)
print('Local parameter path: ' + local_parameter_path)
print('Local config path: ' + local_config_path)
print('Local job template path: ' + local_job_template_path)
print('Local submit job template path: ' + local_submit_job_template_path)

print('Preparing files from templates')
#Generate configs

#Connect via SSH
client = SSHClient()
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
try:
    # sftp.chdir(cluster_src_path)  # Test if cluster_path exists
    print('Working source path exists, checking branch')
except IOError:
    print('Working source path does not exist, pull from Github')

client.disconnect()




