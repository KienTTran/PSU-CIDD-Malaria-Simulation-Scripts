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
      
def cmd_generate_config(working_path,generate_script,parameters):
    return  'cd ' + working_path + \
            '; python3 ' + generate_script + ' ' + parameters
            
#Get Client
client = PipelineClient()

#Read params
params = client.read_parameters('pipeline.yml')
   
#Cluster info
cluster_address = params['ssh']['address']
cluster_username = params['ssh']['username']
cluster_key = params['ssh']['key']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)
cluster_workplace_dir = params['upload']['remote']['workplace_folder']
cluster_project_dir = params['upload']['remote']['project_folder']['name']
cluster_project_bin_dir = params['upload']['remote']['project_folder']['bin']
cluster_project_output_dir = params['upload']['remote']['project_folder']['output']
cluster_project_raw_dir = params['upload']['remote']['project_folder']['raw']
cluster_workplace_path = os.path.join(cluster_home_path,cluster_workplace_dir)
cluster_project_path = os.path.join(cluster_workplace_path,cluster_project_dir)
cluster_project_bin_path = os.path.join(cluster_project_path,cluster_project_bin_dir)
cluster_project_output_path = os.path.join(cluster_project_path,cluster_project_output_dir)
cluster_project_raw_path = os.path.join(cluster_project_path,cluster_project_raw_dir)
print('Cluster workplace: ' + cluster_workplace_path)
print('Cluster project: ' + cluster_project_path)
print('Cluster bin: ' + cluster_project_bin_path)
print('Cluster output: ' + cluster_project_output_path)
print('Cluster raw: ' + cluster_project_raw_path)

#Generate config script
generator_script_name = params['upload']['generator']['script']
generator_script_dir = params['upload']['generator']['folder']
generator_script_parameters = params['upload']['generator']['parameters']
generator_script_parameter_str = ''
if generator_script_parameters != None:
    for parameter in generator_script_parameters:
        generator_script_parameter_str += ' ' + str(parameter)

print('Generate configs & PBS files')
client.run_cmd_locally(cmd_generate_config(generator_script_dir,generator_script_name,generator_script_parameter_str))

local_upload_files = []
cluster_upload_files = []
local_cluster_files = []
local_cluster_pair = ()
local_upload_file_names = params['upload']['files']
if local_upload_file_names == None:
    print('No files to upload')
else:
    for file in local_upload_file_names:
        local_upload = os.path.join(os.path.join(os.getcwd(),generator_script_dir),file)
        local_upload_files.append(local_upload)        
        cluster_upload = ''
        if '.pbs' in file:
            cluster_upload = os.path.join(cluster_project_raw_path,file)
        else:
            cluster_upload = os.path.join(cluster_project_bin_path,file)
        cluster_upload_files.append(cluster_upload)            
        local_cluster_pair = (local_upload,cluster_upload)
        local_cluster_files.append(local_cluster_pair)
    for upload_file in local_upload_files:
        print('Local upload path: ' + upload_file)
    for upload_file in cluster_upload_files:
        print('Cluster upload path: ' + upload_file)
            
#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
try:
    sftp.chdir(cluster_workplace_path) 
    print('Cluster workplace folder exists')
except IOError:
    print('Create cluster workplace folder')
    sftp.mkdir(cluster_workplace_path)    
try:
    sftp.chdir(cluster_project_path) 
    print('Cluster project folder exists')
except IOError:
    print('Create cluster project folder')
    sftp.mkdir(cluster_project_path)    
try:
    sftp.chdir(cluster_project_bin_path) 
    print('Cluster project bin folder exists')
except IOError:
    print('Create cluster project bin folder')
    sftp.mkdir(cluster_project_bin_path)    
try:
    sftp.chdir(cluster_project_output_path) 
    print('Cluster project output folder exists')
except IOError:
    print('Create cluster project output folder')
    sftp.mkdir(cluster_project_output_path) 
try:
    sftp.chdir(cluster_project_raw_path) 
    print('Cluster project raw folder exists')
except IOError:
    print('Create project raw folder')
    sftp.mkdir(cluster_project_raw_path)
    
#Upload
for local_file, cluster_file in local_cluster_files:
    sftp.put(local_file, cluster_file)





