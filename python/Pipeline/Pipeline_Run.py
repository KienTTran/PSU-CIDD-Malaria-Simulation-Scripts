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
      
def cmd_generate_configs(local_path,config_folder,generate_script,parameters):
    return  'cd ' + local_path + \
            '; python3 ' + generate_script + ' ' + parameters + \
            '; tar -cvf ' + config_folder + '.tar.gz' + ' ' + config_folder
    
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
build_workplace_dir = params['build']['remote']['workplace_folder']
build_project_dir = params['build']['remote']['project_folder']
cluster_build_workplace_path = os.path.join(cluster_home_path,build_workplace_dir)
cluster_build_path = os.path.join(os.path.join(cluster_build_workplace_path,build_project_dir),'build/bin')
run_workplace_dir = params['run']['remote']['workplace_folder']
run_project_dir = params['run']['remote']['project_folder']['name']
run_project_bin_dir = params['run']['remote']['project_folder']['bin']
run_project_output_dir = params['run']['remote']['project_folder']['output']
run_project_raw_dir = params['run']['remote']['project_folder']['raw']
run_local_dir = params['run']['local']['folder']
run_generate_config_script = params['run']['local']['generate_config_files']['script']
run_generate_config_folder = params['run']['local']['generate_config_files']['config_folder']
run_generate_config_params = params['run']['local']['generate_config_files']['parameters']

run_exe = params['run']['remote']['exe']
cluster_exe_path = os.path.join(cluster_build_path,run_exe)
cluster_run_workplace_path = os.path.join(cluster_home_path,run_workplace_dir)
cluster_run_project_path = os.path.join(cluster_run_workplace_path,run_project_dir)
print('Build workplace path: ' + cluster_build_workplace_path)
print('Build project path: ' + cluster_build_path)
print('Run workplace path: ' + cluster_run_workplace_path)
print('Run project build path: ' + cluster_run_project_path)
print('Run exe path: ' + cluster_exe_path)
 
generate_path = os.path.join(os.path.join(os.getcwd(),run_local_dir),run_generate_config_script)
generate_config_param_str = ''
for generate_config_param in run_generate_config_params:
    print(generate_config_param)
    generate_config_param_str += ' ' + generate_config_param
generate_config_param_str += ' ' + run_generate_config_folder
generate_config_param_str += ' ' + run_project_dir
generate_config_param_str += ' ' + run_exe
generate_config_param_str += ' ' + cluster_username
print('Generate script path: ' + generate_path)
print('Generate parameters: ' + generate_config_param_str)

print('Preparing files from templates')
#Generate configs
# os.system(cmd_generate_configs(run_local_dir,run_generate_config_folder,run_generate_config_script,generate_config_param_str))

# #Connect via SSH
# client = SSHClient()
# ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

# #Check cluster directories
# try:
#     # sftp.chdir(cluster_src_path)  # Test if cluster_path exists
#     print('Working source path exists, checking branch')
# except IOError:
#     print('Working source path does not exist, pull from Github')

# client.disconnect()




