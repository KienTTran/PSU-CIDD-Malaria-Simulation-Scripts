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
            
def cmd_unzip(working_path,zip_file):
    return  'cd ' + working_path + \
            '; tar -xvf ' + zip_file
                        
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
upload_generator_script_name = params['upload']['generator']['name']
upload_generator_script_dir = params['upload']['generator']['folder']
upload_generator_script_parameters = params['upload']['generator']['parameters']
upload_generator_script_parameter_str = ''
if upload_generator_script_parameters != None:
    for parameter in upload_generator_script_parameters:
        upload_generator_script_parameter_str += ' ' + str(parameter)

#Check using generated files or local files
upload_using_generator = upload_generator_script_name != None
upload_file_pairs = params['upload']['remote']['files']
upload_using_local = upload_file_pairs != None

local_upload_file_path = []
cluster_upload_file_path = []
cluster_upload_mkdir_path = []  
cluster_upload_zip_path = []
local_all_file_exists = True
    
if (upload_using_local and upload_using_generator) or (upload_using_generator and not upload_using_local):
    if not upload_using_local:
        print('Only generator script is in input, please specify upload files')
        exit(0)
    else:
        print('Both local and generator scripts are in input, using generator to produce upload files')
    client.run_cmd_locally(cmd_generate(upload_generator_script_dir,upload_generator_script_name,upload_generator_script_parameter_str))
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
elif upload_using_local and not upload_using_generator:
    print('Only local files are in input, upload using local files')
    for pair in upload_file_pairs:
        if type(pair) == str:
            cluster_upload_mkdir_path.append(os.path.join(cluster_home_path,pair))
        else:
            for key in pair.keys():
                upload_path = key
                upload_files = pair[key]
                cluster_upload_mkdir_path.append(os.path.join(cluster_home_path,upload_path))
                for upload_file in upload_files:
                    local_file_path = os.path.join(local_upload_path,upload_file)
                    cluster_file_path = os.path.join(os.path.join(cluster_home_path,upload_path),upload_file)
                    local_upload_file_path.append(local_file_path)
                    cluster_upload_file_path.append(cluster_file_path)
                    if '.tar.gz' in upload_file:
                        cluster_upload_zip_path.append({os.path.join(cluster_home_path,upload_path) : upload_file})
                    local_all_file_exists = local_all_file_exists and os.path.exists(local_file_path)
                    if not os.path.exists(local_file_path):
                        print(upload_file + ' does not exist')
    if local_all_file_exists:
        for file_path in local_upload_file_path:
            print('Local file path (exists):' + file_path)
    else:
        print('Local files are in input, but does not exist, please check and run again')
        exit(0)
else:
    print('Please supply generator script to produce files to upload')
    exit(0)

for file_path in cluster_upload_file_path:
    print('Cluster file path (upload): ' + file_path)
for file_path in cluster_upload_mkdir_path:
    print('Cluster file path (create): ' + file_path)
    
#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
for file_path in cluster_upload_mkdir_path:
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
    
#Unzip
for pair in cluster_upload_zip_path:
    for key in pair.keys():
        print('Unziping file ' + key + '/' + pair[key])
        client.run_cmd_remotely(cmd_unzip(key,pair[key]))
 
print('Upload pipeline done')
client.disconnect()



