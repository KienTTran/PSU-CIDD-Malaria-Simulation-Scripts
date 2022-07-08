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

#Generate config script
generator_script_name = params['upload']['generator']['name']
generator_script_dir = params['upload']['generator']['folder']
generator_script_parameters = params['upload']['generator']['parameters']
generator_script_parameter_str = ''
if generator_script_parameters != None:
    for parameter in generator_script_parameters:
        generator_script_parameter_str += ' ' + str(parameter)

#Check using generated files or local files
upload_using_generator = generator_script_name != None
upload_file_pairs = params['upload']['remote']['files']
        
local_upload_file_path = []
cluster_upload_file_path = []
cluster_mkdir_path = []  
local_all_file_exists = True
if upload_file_pairs == None:
    print('No files to upload, please check ' + local_upload_path)
    exit(0)
else:    
    for pair in upload_file_pairs:
        if type(pair) == str:
            cluster_mkdir_path.append(os.path.join(cluster_home_path,pair))
        else:
            for key in pair.keys():
                upload_path = key
                upload_files = pair[key]
                cluster_mkdir_path.append(os.path.join(cluster_home_path,upload_path))
                for upload_file in upload_files:
                    local_file_path = os.path.join(local_upload_path,upload_file)
                    cluster_file_path = os.path.join(os.path.join(cluster_home_path,upload_path),upload_file)
                    local_upload_file_path.append(local_file_path)
                    cluster_upload_file_path.append(cluster_file_path)
                    local_all_file_exists = local_all_file_exists and os.path.exists(local_file_path)
                    if not os.path.exists(local_file_path):
                        print(upload_file + ' does not exist, will use generate files using generators')

if local_all_file_exists:
    for file_path in local_upload_file_path:
        print('Local file path (exists):' + file_path)
else:
    print('Generating files using generator')
    client.run_cmd_locally(cmd_generate(generator_script_dir,generator_script_name,generator_script_parameter_str))
    for pair in upload_file_pairs:
        if type(pair) != str:
            for key in pair.keys():
                upload_path = key
                upload_files = pair[key]
                for upload_file in upload_files:
                    local_file_path = os.path.join(local_upload_path,upload_file)
                    local_upload_file_path.append(local_file_path)
                    local_all_file_exists = local_all_file_exists and os.path.exists(local_file_path)
                    if not os.path.exists(local_file_path):
                        print(upload_file + ' does not exist, please check generator outputs')
                    else:
                        print('Local file path (generated): ' + local_file_path)

for file_path in cluster_upload_file_path:
    print('Cluster file path (will upload): ' + file_path)
for file_path in cluster_mkdir_path:
    print('Cluster file path (will create): ' + file_path)
    
#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
for file_path in cluster_mkdir_path:
    client.mkdir_nested(file_path)
    print('Created cluster path: ' + file_path)
    
#Upload
cluster_all_file_exists = True
for local_file, cluster_file in zip(local_upload_file_path,cluster_upload_file_path):
    sftp.put(local_file, cluster_file)
    print('Upload file: ' + file_path)
    cluster_all_file_exists = cluster_all_file_exists and client.print_dir_path_exist_remotely(file_path)

#Final check
if cluster_all_file_exists:
    print('All files uploaded successully to cluster')
else:
    print('Error when uploading files. Please check and try again')





