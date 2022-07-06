# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 11:15:57 2022

@author: kient
"""
import paramiko
import yaml
from getpass import getpass

class SSHClient():
    ssh = paramiko.SSHClient()
    sftp = 0
    params = {} 
    
    def read_parameters(self, input_yaml):
        print("Reading " + input_yaml)
        with open(input_yaml,'r') as file:
            documents = yaml.full_load(file)
            for item, doc in documents.items():
                self.params[item] = doc
                
        return self.params
    
    def disconnect(self):
        self.ssh.close()
        self.sftp.close()
    
    def run_cmd(self,command):
        print(">>> ", command)
        (stdin, stdout, stderr) = self.ssh.exec_command(command,get_pty=True)
        for line in stdout.readlines():
            print(line)
        err = stderr.read().decode()
        if err:
            print(err)
            
    def connect(self, host, username, key):
        if key != 0:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            key = paramiko.Ed25519Key.from_private_key_file(key)
            self.ssh.connect(hostname=host, username=username, pkey=key)
            print('Logged in to server')
        else:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            input_pass = getpass('\nEnter password to login to server: ')
            try:
                self.ssh.connect(host, 22, username, input_pass, allow_agent=False, look_for_keys=False)
                key_auth = str(self.ssh.get_transport())
                if 'awaiting auth' in key_auth:
                    self.ssh.get_transport().auth_interactive_dumb(username, handler=None, submethods='')
            except (paramiko.SSHException) as e:
                print('Cannot login with error ' + str(e))  
                print('Please check password or OTP on mobile')
                exit(0)
                
        self.sftp = self.ssh.open_sftp()
        return self.ssh, self.sftp