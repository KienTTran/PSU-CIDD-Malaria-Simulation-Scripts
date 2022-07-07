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
                        
def cmd_git_pull(home_path, porject_dir, repo_url, repo_branch):
    return  'cd ' + home_path + \
            '; git clone ' + repo_url + " " + porject_dir + " -b " + repo_branch + \
            '; ls -l ' + porject_dir + \
            '; git checkout ' + repo_branch
            
def cmd_git_checkout(porject_dir, repo_branch):
    return  'cd ' + porject_dir + \
            '; git checkout ' + repo_branch
    
def cmd_qsub(cluster_src_path, pbs_file):
    return  'cd ' + cluster_src_path + \
            '; pwd' + \
            '; qsub ' + pbs_file
            
def cmd_build(cluster_src_path, build_script):
    return  'cd ' + cluster_src_path + \
            '; pwd' + \
            '; chmod +x ' + build_script + \
            '; sh ' + build_script
      
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

#Repo info
cluster_workplace_dir = params['build']['remote']['workplace_folder']
cluster_project_dir = params['build']['remote']['project_folder']
cluster_workplace_path = os.path.join(cluster_home_path,cluster_workplace_dir)
cluster_src_path = os.path.join(cluster_workplace_path,cluster_project_dir)
repo_url = params['build']['repo']['url']
repo_branch = params['build']['repo']['branch']
print('Build workplace path: ' + cluster_workplace_path)
print('Build project source path: ' + cluster_src_path)
print('Repo path: ' + repo_url + ' branch: ' + repo_branch)

#Build info
build_local_dir = params['build']['local']['folder']
build_sh_template = params['build']['local']['template']['name']
build_sh_overwrite = params['build']['local']['template']['overwrite']
build_sh_file = build_sh_template.replace('.template','.sh')
build_sh_path = os.path.join(os.path.join(os.getcwd(),build_local_dir),build_sh_file)
print('Build script path: ' + build_sh_path)
 
print('Preparing files from templates')
#Make .sh script
f = open(os.path.join(os.path.join(os.getcwd(),build_local_dir),build_sh_file),'r')
template = f.read()
f.close()
build_sh_file_data = template.replace("#username#",cluster_username)
if os.path.exists(build_sh_path):
    print('Build file exists')
    if build_sh_overwrite == True:
        print('Overwriting build script')
        f = open(build_sh_path,'w')
        f.write(build_sh_file_data)
        f.close()
else:
    print('Writing build script')
    f = open(build_sh_path,'w')
    f.write(build_sh_file_data)
    f.close()
print('Build script done')

#Connect via SSH
ssh,sftp = client.connect(cluster_address, cluster_username, cluster_key)

#Check cluster directories
try:
    sftp.chdir(cluster_src_path)  # Test if cluster_path exists
    print('Working source path exists, checking branch')
    client.run_cmd(cmd_git_checkout(cluster_src_path, repo_branch))
except IOError:
    print('Working source path does not exist, pull from Github')
    client.run_cmd(cmd_git_pull(cluster_workplace_path, cluster_project_dir, repo_url, repo_branch))

#Upload sh script
cluster_script_path = cluster_src_path + "/" + build_sh_file
#Check if remote sh file exists
sftp.chdir(cluster_src_path)
try:
    print(sftp.stat(cluster_script_path))
    print('Build script exists on server')
    if build_sh_overwrite == True:
        print('Overwriting build script on server')
        sftp.put(build_sh_path, cluster_script_path)
except IOError:
    print('Copying build script to server')
    sftp.put(build_sh_path, cluster_script_path)

client.run_cmd(cmd_build(cluster_src_path,build_sh_file))

client.disconnect()




