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

import paramiko
import os
import yaml
from getpass import getpass

def read_parameters():
    params = {}
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
      
params = read_parameters()
print(params)

#Make .sh script
sh_file = 'build.sh'
f = open(params['build_sh_template'][0],'r')
template = f.read()
f.close()
sh_file_data = template.replace("#username#",params['username'])
if os.path.exists(sh_file):
    print('Build file exists')
    if params['build_sh_template'][1] == 'True':
        print('Overwriting build script')
        f = open(sh_file,'w')
        f.write(sh_file_data)
        f.close()
else:
    print('Writing build script')
    f = open(sh_file,'w')
    f.write(sh_file_data)
    f.close()
    
#Make pbs script
pbs_file = 'build.pbs'
f = open(params['build_pbs_template'][0],'r')
template = f.read()
f.close()
pbs_file_data = template.replace("#buildscript#",sh_file)
if os.path.exists(pbs_file):
    print('PBS file exists')
    if params['build_pbs_template'][1] == 'True':
        print('Overwriting PBS file')
        f = open(pbs_file,'w')
        f.write(pbs_file_data)
        f.close()
else:
    print('Writing PBS file')
    f = open(pbs_file,'w')
    f.write(pbs_file_data)
    f.close()
    
#Connect via SSH
ssh = paramiko.SSHClient()
if params['key'] != '':
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.Ed25519Key.from_private_key_file(params['key'])
    ssh.connect(hostname=params['host'], username=params['username'], pkey=key)
    print('Logged in to server')
else:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    input_pass = getpass('\nEnter password to login to server: ')
    try:
        ssh.connect(params['host'], 22, params['username'], input_pass)
    except (paramiko.SSHException) as e:
        print('Cannot login with error ' + str(e))  
        print('Please check password or OTP on mobile')
        exit(0)
sftp = ssh.open_sftp()

remotepath_src = "/storage/home/" + params['username'][0] + "/" + params['username'] + "/Github/"
remotepath_work = "/storage/work/" + params['username'][0] + "/" + params['username'] + "/"
project_name = "PSU-CIDD-Malaria-Simulation-Dev"
remote_project_src_path = os.path.join(remotepath_src,project_name)
# print(remote_project_src_path)

#Upload sh script
local_script_path = os.path.join(os.getcwd(),sh_file)
remote_script_path = remote_project_src_path + "/" + sh_file
#Check if remote sh file exists
sftp.chdir(remote_project_src_path)
try:
    print(sftp.stat(remote_script_path))
    print('Build script exists on server')
    if params['build_sh_template'][1] == 'True':
        print('Overwriting build script on server')
        sftp.put(local_script_path, remote_script_path)
except IOError:
    print('Copying build script to server')
    sftp.put(local_script_path, remote_script_path)

#Upload pbs script
local_script_path = os.path.join(os.getcwd(),pbs_file)
remote_script_path = remote_project_src_path + "/" + pbs_file
#Check if remote pbs file exists 
try:
    print(sftp.stat(remote_script_path))
    print('PBS script exists on server')
    if params['build_pbs_template'][1] == 'True':
        print('Overwriting PBS file on server')
        sftp.put(local_script_path, remote_script_path)
except IOError:
    print('Copying PBS file to server')
    sftp.put(local_script_path, remote_script_path)
    
commands =  [
            '; cd ' + remote_project_src_path + \
            '; pwd' + \
            '; qsub ' + pbs_file
            ];

for command in commands:
    print(">>> ", command)
    (stdin, stdout, stderr) = ssh.exec_command(command,get_pty=True)
    for line in stdout.readlines():
        print(line)
    err = stderr.read().decode()
    if err:
        print(err)

sftp.close()
ssh.close()




