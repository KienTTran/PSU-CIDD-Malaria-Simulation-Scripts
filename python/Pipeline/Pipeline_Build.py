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
                        

def cmd_generate(working_path,script_name,parameters):
    return  'cd ' + working_path + \
            '; python3 ' + script_name + ' ' + parameters
            
def cmd_git_pull(project_path, build_repo_url, build_repo_branch):
    project_name = project_path.split('/')[-1]
    project_parent_path = project_path.replace(project_name,'')
    return  'cd ' + project_parent_path + \
            '; git clone ' + build_repo_url + " " + project_name + " -b " + build_repo_branch + \
            '; ls -l ' + project_name + \
            '; cd ' + project_name + \
            '; git checkout ' + build_repo_branch
            
def cmd_git_checkout(project_path, build_repo_branch):
    return  'cd ' + project_path + \
            '; git checkout ' + build_repo_branch
                
def cmd_build(project_path, build_script_name, parameters):
    return  'cd ' + project_path + \
            '; pwd' + \
            '; chmod +x ' + build_script_name + \
            '; sh ' + build_script_name + ' ' + parameters
      
#Get Client
client = PipelineClient()

#Read params
params = client.read_parameters('pipeline.yml')
   
#Local info
local_build_dir = params['build']['local']
local_build_path = os.path.join(os.getcwd(),local_build_dir)

#ssh info
cluster_address = params['ssh']['address']
cluster_username = params['ssh']['username']
cluster_key = params['ssh']['key']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)

#Script info
script_name = params['build']['script']['name']
if script_name == None:
    script_name = 'build.sh'
script_working_dir = params['build']['script']['folder']
script_working_path = os.path.join(cluster_home_path,script_working_dir)
script_parameters = params['build']['script']['parameters']
script_parameter_str = ''
if script_parameters != None:
    for parameter in script_parameters:
        script_parameter_str += ' ' + str(parameter)

#Cluster info
cluster_project_dir = params['project']['folder']
cluster_project_path = os.path.join(cluster_home_path,cluster_project_dir)
cluster_script_path = script_working_path + "/" + script_name
cluster_target = params['project']['exe']
cluster_target_path = os.path.join(cluster_project_path,cluster_target)
print('Cluster project path: ' + cluster_project_path)
print('Cluster target path: ' + cluster_target_path)

#Repo info            
build_repo_url = params['build']['repo']['url']
build_repo_branch = params['build']['repo']['branch']
print('Repo path: ' + build_repo_url + ' branch: ' + build_repo_branch)

#Generator info   
build_generator_script_name = params['build']['generator']['name']
build_generator_script_dir = params['build']['generator']['folder']
build_generator_script_parameters = params['build']['generator']['parameters']
build_generator_script_parameter_str = ''
if build_generator_script_parameters != None:
    for parameter in build_generator_script_parameters:
        build_generator_script_parameter_str += ' ' + str(parameter)
    build_generator_script_parameter_str += ' ' + script_name
        
#Check local script or generator available
build_using_local = script_name != None
build_using_generator = build_generator_script_name != None
if (build_using_generator and build_using_local) or (build_using_generator and not build_using_local):
    if not build_using_local:
        print('Only generator script is in input, will generate build script with default name: ' + script_name)
    else:
        print('Both local and generator scripts are in input, will use generator to generate build script with name ' + script_name) 
    client.run_cmd_locally(cmd_generate(build_generator_script_dir,build_generator_script_name,build_generator_script_parameter_str))
    local_script_path = os.path.join(os.path.join(os.getcwd(),build_generator_script_dir),script_name)
elif build_using_local and not build_using_generator:
    local_script_path = os.path.join(local_build_path,script_name)
    if os.path.exists(local_script_path):
        print('Only local script is in input, will upload and use script: ' + script_name)
    else:
        print('Local script is in input, but does not exist, please check and run again')
        exit(0)
else:
    print('Please supply at least local script or generator script to build')
    exit(0)

print('Local build script path: ' + local_script_path)
print('Cluster build script path: ' + cluster_script_path)

#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
try:
    sftp.chdir(cluster_project_path)  # Test if cluster_path exists
    print('Working source path exists, checking branch')
    client.run_cmd_remotely(cmd_git_checkout(cluster_project_path, build_repo_branch))
except IOError:
    print('Working source path does not exist, pull from Github')
    client.mkdir_nested(cluster_project_path)
    client.run_cmd_remotely(cmd_git_pull(cluster_project_path, build_repo_url, build_repo_branch))
    
#Upload sh script
sftp.chdir(script_working_path)
print('Writing build script on server')
sftp.put(local_script_path, cluster_script_path)
client.run_cmd_remotely(cmd_build(cluster_project_path,script_name,script_parameter_str))

#Check after build
if client.print_file_path_exist_remotely(cluster_target_path):
    print('Target built successfully on cluster')
else:
    print('Error building target on cluster. Please check and try again')

print('Build pipeline done')
client.disconnect()




