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
                        

def cmd_generate_build_script(working_path,script_name,parameters):
    return  'cd ' + working_path + \
            '; python3 ' + script_name + ' ' + parameters
            
def cmd_git_pull(cluster_home_path, cluster_project_dir, repo_url, repo_branch):
    return  'cd ' + cluster_home_path + \
            '; git clone ' + repo_url + " " + cluster_project_dir + " -b " + repo_branch + \
            '; ls -l ' + cluster_project_dir + \
            '; git checkout ' + repo_branch
            
def cmd_git_checkout(porject_dir, repo_branch):
    return  'cd ' + porject_dir + \
            '; git checkout ' + repo_branch
                
def cmd_build(cluster_project_path, build_script_name, parameters):
    return  'cd ' + cluster_project_path + \
            '; pwd' + \
            '; chmod +x ' + build_script_name + \
            '; sh ' + build_script_name + ' ' + parameters
      
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
cluster_workplace_dir = params['build']['remote']['workplace_folder']
cluster_project_dir = params['build']['remote']['project_folder']
cluster_workplace_path = os.path.join(cluster_home_path,cluster_workplace_dir)
cluster_project_path = os.path.join(cluster_workplace_path,cluster_project_dir)
script_name = params['build']['script']['name']
script_parameters = params['build']['script']['parameters']
script_parameter_str = ''
if script_parameters != None:
    for parameter in script_parameters:
        script_parameter_str += ' ' + str(parameter)
            
repo_url = params['build']['repo']['url']
repo_branch = params['build']['repo']['branch']
print('CLuster workplace path: ' + cluster_workplace_path)
print('Cluster project source path: ' + cluster_project_path)
print('Repo path: ' + repo_url + ' branch: ' + repo_branch)
    
print('Generating build script')
generator_script_name = params['build']['generator']['script']
generator_script_dir = params['build']['generator']['folder']
generator_script_parameters = params['build']['generator']['parameters']
generator_script_parameter_str = ''
if generator_script_parameters != None:
    for parameter in generator_script_parameters:
        generator_script_parameter_str += ' ' + str(parameter)
    generator_script_parameter_str += ' ' + script_name
client.run_cmd_locally(cmd_generate_build_script(generator_script_dir,generator_script_name,generator_script_parameter_str))
local_script_path = os.path.join(os.path.join(os.getcwd(),generator_script_dir),script_name)
print('Generated build script: ' + local_script_path)

#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
try:
    sftp.chdir(cluster_project_path)  # Test if cluster_path exists
    print('Working source path exists, checking branch')
    client.run_cmd_remotely(cmd_git_checkout(cluster_project_path, repo_branch))
except IOError:
    print('Working source path does not exist, pull from Github')
    client.run_cmd_remotely(cmd_git_pull(cluster_workplace_path, cluster_project_dir, repo_url, repo_branch))
    
#Upload sh script
cluster_script_path = cluster_project_path + "/" + script_name
sftp.chdir(cluster_project_path)
print('Writing build script on server')
sftp.put(local_script_path, cluster_script_path)
client.run_cmd_remotely(cmd_build(cluster_project_path,script_name,script_parameter_str))

client.disconnect()




