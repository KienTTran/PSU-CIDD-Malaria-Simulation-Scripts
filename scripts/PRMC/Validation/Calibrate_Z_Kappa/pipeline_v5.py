# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 10:16:32 2022

@author: kient
"""

import io
import kfp.components as comp
import kfp
from typing import NamedTuple

client = kfp.Client(host='http://172.28.86.153:31492/')

download_op = kfp.components.load_component_from_url(
'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/contrib/web/Download/component.yaml')

def step_1_parse_config(pipeline_config: comp.InputArtifact()) -> NamedTuple('outputs', [
                                                                                ('remote_auth', dict),
                                                                                ('remote_repo', list),
                                                                                ('remote_sims', list),
                                                                                ('remote_binaries', list),
                                                                                ('remote_dirs', list),
                                                                                ('remote_files', list),
                                                                                ('remote_storages', list),
                                                                                ('remote_tasks', list),
                                                                                ('remote_plots', list)
                                                                                ]):
    import yaml
    import os
    from collections import namedtuple
    import requests
    
    print('Parsing pipeline config')
    
    params = 0
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
            
    def parse_auth(keyword):
        remote_auth = {}
        #Download key
        headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
        r = requests.get(params['auth']['ssh_key_url'], stream=True, headers=headers)
        for chunk in r.iter_content(chunk_size=1024):
            remote_auth['ssh_key'] = chunk.decode('utf-8')
        remote_auth['ssh_address'] = params['auth']['ssh_address']
        remote_auth['ssh_username'] = params['auth']['ssh_username']
        remote_auth['ssh_duo_option'] = params['auth']['ssh_duo_option']
        remote_home_path = "/storage/home/" + remote_auth['ssh_username'][0] + "/" + remote_auth['ssh_username']
        remote_auth['minio_address'] = params['auth']['minio_address']
        remote_auth['minio_key'] = params['auth']['minio_key']
        remote_auth['minio_secret'] = params['auth']['minio_secret']
        return remote_auth,remote_home_path
                
    def add_dict_to_array(array,project_name,sim_name,dict_to_add):
        project_keys = []
        for project in array:
            for project_key in project.keys():
                project_keys.append(project_key)
        
        if project_name in project_keys:
            for project in array:
                if project_name in project.keys():
                    project[project_name].append({sim_name : dict_to_add})
        else:
            array.append({project_name : [{sim_name : dict_to_add}]})

    def add_array_to_array(array,project_name,sim_name,array_to_add,array_key=None):
        project_keys = []
        for project in array:
            for project_key in project.keys():
                project_keys.append(project_key)
                
        if array_key == None:
            if project_name in project_keys:
                for project in array:
                    if project_name in project.keys():
                        project[project_name].append({sim_name : array_to_add})
            else:
                array.append({project_name : [{sim_name : array_to_add}]})
        else:
            # print('Input: ',array_key,project_name,sim_name, project_keys)
            if project_name not in project_keys:
                # print(project_name + ' not available, adding')
                array.append({project_name : [{sim_name : {array_key : array_to_add}}]})
            else:
                for project in array:
                    # print(' Checking ' + project_name)
                    if project_name in project.keys():
                        sim_keys = []
                        for simulation in project[project_name]:
                            for sim_key in simulation.keys():
                                sim_keys.append(sim_key)
                                
                        if sim_name not in sim_keys: 
                            # print('   ' + sim_name + ' not in project, adding')
                            project[project_name].append({sim_name : {array_key : array_to_add}})
                            break
                        else:
                            # print(project_name,sim_keys)                            
                            for simulation in project[project_name]:
                                # print('  Checking ' + project_name + ' ' + sim_name)                        
                                if sim_name in simulation.keys():
                                    # print('   ' + sim_name + ' in project')
                                    if array_key in simulation[sim_name].keys():
                                        # print('    Array ' + array_key + ' in ' + sim_name)
                                        for item in array_to_add:
                                            simulation[sim_name][array_key].append(item)
                                    else:
                                        # print('    Array ' + str(array_key + ' not in ' + sim_name) + ' adding')
                                        simulation[sim_name][array_key] = array_to_add
                                        break
            
    def parse_simulation(keyword, remote_home_path):
        remote_repo = []
        remote_sims = []
        remote_binaries = []
        remote_dirs = []
        remote_files = []
        remote_work_dirs = {'bin':'bin','input':'input','output':'output','log':'log','script':'script','plot':'plot'}
        remote_storages = []
        for project in params[keyword]:
            if type(project) == str:
                print('Project is empty')
            else:
                for project_name in project.keys():
                    if project[project_name] == None:
                        print('Project is empty')
                    else:
                        for simulation in project[project_name]:
                            for sim_name in simulation.keys():
                                if simulation[sim_name] == None:
                                    print('Simulation is empty')
                                else: 
                                    simulation_data = { 'home_path': remote_home_path,
                                                        'build': simulation[sim_name]['build'],
                                                        'build_path': os.path.join(remote_home_path,simulation[sim_name]['build']),
                                                        'build_script': simulation[sim_name]['script'],
                                                        'build_script_path': os.path.join(os.path.join(remote_home_path,simulation[sim_name]['build']),simulation[sim_name]['script']),
                                                        'build_bin': simulation[sim_name]['binary'],
                                                        'build_bin_path': os.path.join(os.path.join(remote_home_path,simulation[sim_name]['build']),simulation[sim_name]['binary']),
                                                        'work': simulation[sim_name]['work'],
                                                        'work_dirs' : remote_work_dirs,
                                                        'work_path': os.path.join(os.path.join(remote_home_path,simulation[sim_name]['work']),os.path.join(project_name,sim_name)),
                                                        'local_path' : os.path.join(simulation[sim_name]['local'],os.path.join(project_name,sim_name)),
                                                        'check_interval' : str(simulation[sim_name]['check_interval']),
                                                        'using_tar' : str(simulation[sim_name]['using_tar']),
                                                        'using_storage' : str(simulation[sim_name]['using_storage'])
                                                        }
                                    add_dict_to_array(remote_sims, project_name, sim_name, simulation_data)
                                    sim_repo = simulation[sim_name]['repo']
                                    if sim_repo == None:
                                        print('Repo is empty')
                                    else:
                                        sim_repo_url = simulation[sim_name]['repo']['url']
                                        if sim_repo_url == None:
                                            print('Repo URL is empty')
                                        else:
                                            sim_repo_branch = simulation[sim_name]['repo']['branch']
                                            sim_repo_git = ''
                                            if sim_repo_branch == None:
                                                sim_repo_git = sim_repo_url
                                            else:
                                                sim_repo_git = sim_repo_url + ' -b ' + str(sim_repo_branch)
                                                add_dict_to_array(remote_repo,project_name,sim_name,{os.path.join(remote_home_path,simulation[sim_name]['build']):sim_repo_git})
                                    
        for project in remote_sims:
            for project_name in project.keys():
                for simulation in project[project_name]:
                    for sim_name in simulation.keys():
                        sim_dirs = []
                        data_files = []
                        for work_dir in remote_work_dirs.keys():
                            sim_dirs.append({remote_work_dirs[work_dir]:os.path.join(simulation[sim_name]['work_path'],remote_work_dirs[work_dir])})
                            if simulation[sim_name]['using_tar'] == 'True':
                                data_files.append({remote_work_dirs[work_dir]:{os.path.join(simulation[sim_name]['work_path'],remote_work_dirs[work_dir]+'.tar.gz'):
                                                                                os.path.join(project_name,os.path.join(sim_name,remote_work_dirs[work_dir]+'.tar.gz'))}})
                            else:
                                data_files.append({remote_work_dirs[work_dir]:{os.path.join(simulation[sim_name]['work_path'],remote_work_dirs[work_dir]):
                                                                                os.path.join(project_name,os.path.join(sim_name,remote_work_dirs[work_dir]))}})
                        add_array_to_array(remote_dirs, project_name,sim_name,sim_dirs,keyword)
                        add_array_to_array(remote_storages,project_name,sim_name,data_files)
                        project_build_bin_path = os.path.join(os.path.join(remote_home_path,simulation[sim_name]['build']),simulation[sim_name]['build_bin'])
                        project_work_bin_path = os.path.join(os.path.join(simulation[sim_name]['work_path'],remote_work_dirs['bin']),simulation[sim_name]['build_bin'].split('/')[-1])
                        add_dict_to_array(remote_binaries,project_name,sim_name,{project_build_bin_path:project_work_bin_path})
        return remote_repo, remote_sims, remote_binaries, remote_dirs, remote_files, remote_storages

    def parse_commander(keyword, remote_auth, remote_sims, remote_dirs, remote_files):
        commanders = []
        for project_index,project in enumerate(params[keyword]):
            if type(project) == str:
                print('Project is empty')
            else:
                for project_name in project.keys():
                    if project[project_name] == None:
                        print('Project is empty')
                    else:
                        for sim_index,simulation in enumerate(project[project_name]):
                            script_with_parameters = []
                            sim_files = []
                            for sim_name in simulation.keys():
                                if simulation[sim_name] == None:
                                    print('Simulation is empty')
                                else: 
                                    for task_index,tasks in enumerate(simulation[sim_name]):
                                        for scripts in tasks.keys():
                                            for script_index,script in enumerate(tasks[scripts]):
                                                if script == None:
                                                    print('Script is empty')
                                                else:
                                                    for script_type in script.keys():
                                                        if script_type != 'script':
                                                            print('No script keyword')
                                                        else:
                                                            try:
                                                                script_full = ''
                                                                script_name = ''
                                                                script_folder = ''
                                                                script_folder = ''
                                                                script_path = ''
                                                                script_folder = script[script_type]['path']
                                                                remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                                                                remote_storage = remote_storages[project_index][project_name][sim_index][sim_name]
                                                                if script_folder == 'None' or script_folder == None or script_folder == '':
                                                                    script_folder = 'None'
                                                                    script_path = script_folder
                                                                else:
                                                                    script_path = os.path.join(remote_sim['work_path'],script_folder)
                                                                    add_array_to_array(remote_dirs, project_name, sim_name, [{script_folder:script_path}],keyword)
                                                                if 'http' in script[script_type]['source']:
                                                                    sim_files.append({script_path : script[script_type]['source']})
                                                                    script_name = script[script_type]['source'].split('/')[-1]
                                                                else:
                                                                    script_name = script[script_type]['source']
                                                                parameter_str = ''
                                                                if script[script_type]['appended']:
                                                                    parameter_str += ' ' + "\"" + str(remote_auth) + "\""
                                                                    parameter_str += ' ' + "\"" + str(remote_sim) + "\""
                                                                    parameter_str += ' ' + "\"" + str(remote_storage) + "\""
                                                                    parameter_str += ' ' + "\"" + str(scripts) + "\""
                                                                    parameter_str += ' ' + "\"" + str(script_path) + "\""
                                                                try:
                                                                    script_parameters = script[script_type]['parameter']
                                                                    if script_parameters != None:
                                                                        for parameter in script_parameters:
                                                                            if 'http' in parameter:
                                                                                sim_files.append({script_path : parameter})
                                                                                parameter_str += ' ' + parameter.split('/')[-1]
                                                                            else:
                                                                                parameter_str += ' ' + parameter
                                                                    else:
                                                                        print(script_name + ' has no parameters')     
                                                                except Exception as e:
                                                                    print('Missing: ' + str(e) + ', use empty parameters')
                                                                script_exe = ''
                                                                if script_name != None and script_name != '':
                                                                    script_ext = script_name.split('.')[-1]
                                                                    if script_ext == 'py':
                                                                        script_exe = 'python3'
                                                                    elif script_ext == 'sh':
                                                                        script_exe = 'sh'
                                                                else:
                                                                    print('Script name is empty, skipped')
                                                                script_full = script_exe + ' ' + script_name + parameter_str
                                                                script_with_parameters.append({script_path:{scripts:script_full}})
                                                            except Exception as e:
                                                                print('Missing: ' + str(e) + ', skipped')
                                add_dict_to_array(commanders, project_name, sim_name, script_with_parameters)
                                add_array_to_array(remote_files, project_name, sim_name, sim_files,keyword)
        return commanders        

    remote_auth,remote_home_path = parse_auth('auth')
    remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages = parse_simulation('simulation',remote_home_path)
    remote_tasks = parse_commander('task',remote_auth,remote_sims,remote_dirs,remote_files)
    remote_plots = parse_commander('plot',remote_auth,remote_sims,remote_dirs,remote_files)

    for key in remote_auth.keys():
        print('ssh ' + key + ' ' + str(remote_auth[key]))
        
    for project in remote_sims:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for key in simulation[sim_name].keys():
                        print(project_name + ': sim ' + sim_name + ': key: ' + key  + ': ' + str(simulation[sim_name][key]))
                    
    for project in remote_repo:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for key in simulation[sim_name].keys():
                        print(project_name + ': sim ' + sim_name + ': git clone ' + str(simulation[sim_name][key]) + ' ' + key)
                        
    for project in remote_binaries:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for key in simulation[sim_name].keys():
                        print(project_name + ': sim ' + sim_name + ': cp ' + key + ' ' + str(simulation[sim_name][key]))

    for project in remote_dirs:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for field in simulation[sim_name].keys():
                        for dirs in simulation[sim_name][field]:
                            for working_path in dirs.keys():
                                print(project_name + ': sim ' + sim_name + ': field: ' + field + ': remote mkdir nest ' +  dirs[working_path])                       
            
    for project in remote_files:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for field in simulation[sim_name].keys():
                        for files in simulation[sim_name][field]:
                            for working_path in files.keys():
                                print(project_name + ': sim ' + sim_name + ': field: ' + field + ': wget ' + files[working_path] + ' -P ' + working_path + ' -N')
            
    for project in remote_storages:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                        for data in simulation[sim_name]:
                            for work_dir in data.keys():
                                for remote_path in data[work_dir].keys():
                                    print(project_name + ': sim ' + sim_name + ': work dir is: ' + work_dir + ': remote is ' + remote_path + ' storage is ' + str(data[work_dir][remote_path]))
                    
    for project in remote_tasks:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for tasks in simulation[sim_name]:
                        for task_path in tasks.keys():
                            for script_name in tasks[task_path].keys():
                                print(project_name + ': sim ' + sim_name + ': task ' + script_name + ': cd ' + task_path + ' && run ' + tasks[task_path][script_name])
                                
    for project in remote_plots:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for plots in simulation[sim_name]:
                        for plot_path in plots.keys():
                            for figure_name in plots[plot_path].keys():
                                print(project_name + ': sim ' + sim_name + ': figure ' + figure_name + ': cd ' + plot_path + ' && run ' + plots[plot_path][figure_name])     

    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])  
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)

def step_2_make_dirs(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import subprocess
    import tarfile
    from stat import S_ISDIR, S_ISREG 

    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close()
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                    
         
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
                   
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
    
    #Make dirs
    for project in remote_dirs:
        for project_name in project.keys():
            for simulation in project[project_name]:
                for sim_name in simulation.keys():
                    for field in simulation[sim_name].keys():
                        for dirs in simulation[sim_name][field]:
                            for working_path in dirs.keys():
                                print(project_name + ': sim ' + sim_name + ': field: ' + field + ': remote mkdir nest ' +  dirs[working_path])
                                if not pipeline_client.is_dir_path_existed_remotely(dirs[working_path]):
                                    pipeline_client.mkdir_nested_remotely(dirs[working_path])
                                else:
                                    print(dirs[working_path] + ' already exists')

    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])  
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)
                                                 
def step_3_build_binary(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import tarfile
    from stat import S_ISDIR, S_ISREG 
    
    def cmd_git_clone(repo_info, dir_dst):
        return 'git clone ' + repo_info + ' ' + dir_dst

    def cmd_git_checkout(repo_info, dir_dst):
        branch = repo_info.split('-b ')[-1]
        return 'cd ' + dir_dst + ' && git checkout ' + branch + ' && git pull'
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close() 
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                    
         
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
       
    import minio
    from minio import Minio
    import re
    import time
    class StorageClient():
        minio_client = 0 
       
        def connect(self,host='host:port',
                  username='key',
                  password='secret'):
            self.minio_client = Minio(endpoint=host,
                    access_key=username,
                    secret_key=password,
                    secure=False)
          
        def make_bucket(self,bucket_name):
            try:
              found = self.minio_client.bucket_exists(bucket_name)
              if not found:
                  self.minio_client.make_bucket(bucket_name)
              else:
                  print('Bucket ' + bucket_name + ' already exists')
            except minio.error.BucketAlreadyExists:
              pass
            except minio.error.BucketAlreadyOwnedByYou:
              pass
              
        def is_file_existed(self,bucket_name,file_path):
            try:
                stat = self.minio_client.stat_object(storage_bucket, file_path)
                print(os.path.join(bucket_name,stat.object_name) + ' exists')
                return True
            except Exception as err:
                print(os.path.join(bucket_name,file_path) + ' does not exist')
                return False
                
        def upload_from_path(self,bucket_name,local_path,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(local_path,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(local_path,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(local_path,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(local_path,file_path)))
                    else:
                        if sub_folder == None:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path))
                        else:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path),sub_folder)
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,local_path,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + local_path)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,local_path),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,local_path))
          
        def upload_from_path_and_rename(self,bucket_name,local_path,new_name,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(new_name,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(new_name,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(new_name,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(new_name,file_path)))                    
                    else:
                        if sub_folder == None:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path))
                        else:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path),sub_folder)
                        
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,new_name,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + new_name)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,new_name),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,new_name))
                    
        def download_from_path(self,bucket_name,remote_path,local_path=None):
            dest_path = ''
            if local_path == None:
                dest_path = os.getcwd()
            else:
                dest_path = local_path
                
            print(os.path.join(dest_path,remote_path))
            if not os.path.isdir(os.path.join(dest_path,remote_path)):
                os.makedirs(os.path.join(dest_path,remote_path), exist_ok=True)
                print('made dir ' + remote_path)
            objects = storage_client.minio_client.list_objects(bucket_name, prefix=remote_path,recursive=True)
            for obj in objects:
                self.download_file_path(bucket_name, obj.object_name, os.path.join(dest_path,obj.object_name))  
                print('Downloaded from ' + os.path.join(bucket_name,obj.object_name) + ' to ' + os.path.join(dest_path,obj.object_name))
        
        def upload_file_path(self,bucket_name,file_path,local_path,sub_folder=None):
            if sub_folder == None:
                self.minio_client.fput_object(bucket_name,file_path,local_path)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from ' + local_path)
            else:
                self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,file_path),local_path)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from ' + local_path)
          
        def download_file_path(self,bucket_name,file_path,local_path):
            self.minio_client.fget_object(bucket_name,file_path,local_path)
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to ' + local_path)        
            
        def upload_file(self,bucket_name,file_path,data,length,sub_folder=None):
            if sub_folder == None:
                self.minio_client.put_object(bucket_name, file_path, data, length)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from buffer')
            else:
                self.minio_client.put_object(bucket_name, os.path.join(sub_folder,file_path), data, length)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from buffer')
          
        def download_file(self,bucket_name,file_path):
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to buffer')
            return self.minio_client.get_object(bucket_name, file_path)
            
        def upload_folder_from_sftp(self,pipeline_client,sftp_folder_parent_path,sftp_folder_name,bucket_name,file_path,sub_folder=None):
            item_list = pipeline_client.sftp.listdir_attr(os.path.join(sftp_folder_parent_path,sftp_folder_name))
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    print('dir ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    self.upload_folder_from_sftp(pipeline_client,os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename,bucket_name,os.path.join(file_path,item.filename))
                else:
                    print('file ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    with pipeline_client.sftp.open(os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename), "rb") as fl:
                        fl.prefetch()
                        if sub_folder == None:
                            self.upload_file(bucket_name, os.path.join(file_path,item.filename), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(file_path,item.filename))
                        else:
                            self.upload_file(bucket_name, os.path.join(sub_folder,os.path.join(file_path,item.filename)), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(file_path,item.filename)))
                    
        def transfer_folder_to_sftp(self,pipeline_client,bucket_name,folder,remote_parent_path):
            objects = self.minio_client.list_objects(bucket_name, prefix=folder)
            for obj in objects:
                if obj.is_dir:
                    print('dir ',os.path.join(bucket_name,obj.object_name),os.path.join(remote_parent_path,obj.object_name))
                    if not pipeline_client.is_dir_path_existed_remotely(os.path.join(remote_parent_path,obj.object_name)):
                        pipeline_client.mkdir_nested_remotely(os.path.join(remote_parent_path,obj.object_name))                
                    print(os.path.join(bucket_name,obj.object_name) + ' is dir')
                    self.transfer_folder_to_sftp(pipeline_client,bucket_name,obj.object_name,remote_parent_path)
                else:
                    print('file ',bucket_name + '/' + obj.object_name,os.path.join(remote_parent_path,obj.object_name))
                    file = self.download_file(bucket_name, obj.object_name)
                    pipeline_client.sftp.putfo(file, os.path.join(remote_parent_path,obj.object_name))
                    print('Transferred from ' + bucket_name + '/' + obj.object_name + ' to ' + os.path.join(remote_parent_path,obj.object_name))
                    
        def upload_file_from_sftp(self,pipeline_client,sftp_file_path,bucket_name,sub_folder=None):
            with pipeline_client.sftp.open(sftp_file_path, "rb") as fl:
                fl.prefetch()
                if sub_folder == None:
                    self.upload_file(bucket_name, sftp_file_path.split('/')[-1], fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + bucket_name + '/' + sftp_file_path.split('/')[-1])  
                else:
                    self.upload_file(bucket_name, os.path.join(sub_folder,sftp_file_path.split('/')[-1]), fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + os.path.join(bucket_name,os.path.join(sub_folder,sftp_file_path.split('/')[-1])))          
                    
        def transfer_file_to_sftp(self,pipeline_client,bucket_name,file_path,remote_path):
            file = self.download_file(bucket_name, file_path)
            pipeline_client.sftp.putfo(file, remote_path)
            print('Transferred from ' + bucket_name + '/' + remote_path + ' to ' + remote_path)
                    
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
            
    #Get repo
    for project_index,project in enumerate(remote_repo):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for working_path in simulation[sim_name].keys():
                        print(project_name + ': sim ' + sim_name + ': git clone ' + str(simulation[sim_name][working_path]) + ' ' + working_path)
                        if pipeline_client.is_dir_path_existed_remotely(working_path):
                             pipeline_client.run_cmd_remotely(cmd_git_checkout(simulation[sim_name][working_path],working_path))
                        else:
                             pipeline_client.run_cmd_remotely(cmd_git_clone(simulation[sim_name][working_path],working_path))
                             
                        #Build project
                        #Edit build script
                        remote_build_folder = remote_sim['build_path']
                        remote_build_script = remote_sim['build_script']
                        cmd_cd_build = 'cd ' + remote_build_folder
                        cmd_replace_username = 'sed -i \'s/#username#/' + remote_auth['ssh_username'] + '/g\' ' + remote_build_script
                        cmd_run_build_script = 'chmod +x ' + remote_build_script + ' && ./' + remote_build_script
                              
                        #Build
                        cmd_build_flow = cmd_cd_build + ' && ' + \
                             cmd_replace_username + ' && ' + \
                             cmd_run_build_script                 
                        print(cmd_build_flow)
                        if pipeline_client.is_file_path_existed_remotely(os.path.join(remote_build_folder,remote_build_script)):
                            pipeline_client.run_cmd_remotely(cmd_build_flow)
                        else:
                           print('No ' + remote_build_script + ' in ' + remote_build_folder)
                    
    #Copy bin to remote
    for project_index,project in enumerate(remote_binaries):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for key in simulation[sim_name].keys():
                        print(project_name + ': sim ' + sim_name + ': cp ' + key + ' ' + str(simulation[sim_name][key]))
                        cmd_cp_bin = 'cp ' + key + ' ' + simulation[sim_name][key]
                        pipeline_client.run_cmd_remotely(cmd_cp_bin)
                        
                        # Upload bin folder                  
                        print('Project ' + project_name)                 
                        remote_work_name = project_name
                        storage_client = StorageClient()
                        storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
                        storage_bucket = remote_work_name.lower()
                        storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
                        storage_client.make_bucket(storage_bucket)
                            
                        if remote_sim['using_storage'] == 'True':
                            if remote_sim['using_tar'] == 'True':
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], remote_sim['work_dirs']['bin'])
                                storage_client.upload_file_from_sftp(pipeline_client, 
                                                                     os.path.join(remote_sim['work_path'],remote_sim['work_dirs']['bin']+'.tar.gz'), 
                                                                     storage_bucket,
                                                                     sim_name)
                            else:
                                storage_client.upload_folder_from_sftp(pipeline_client, 
                                                                    remote_sim['work_path'],
                                                                    remote_sim['work_dirs']['bin'],
                                                                    storage_bucket,
                                                                    remote_sim['work_dirs']['bin'],
                                                                    sim_name)
                        else:
                            if remote_sim['using_tar'] == 'True':
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], remote_sim['work_dirs']['bin'])
                            else:
                                print('Not using tar or storage')
                            

    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])    
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)

def step_4_run_tasks(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import tarfile
    import os.path
    import subprocess
    import json
    from stat import S_ISDIR, S_ISREG 
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close()
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                
        
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
       
    import minio
    from minio import Minio
    import re
    import time
    class StorageClient():
        minio_client = 0 
       
        def connect(self,host='host:port',
                  username='key',
                  password='secret'):
            self.minio_client = Minio(endpoint=host,
                    access_key=username,
                    secret_key=password,
                    secure=False)
          
        def make_bucket(self,bucket_name):
            try:
              found = self.minio_client.bucket_exists(bucket_name)
              if not found:
                  self.minio_client.make_bucket(bucket_name)
              else:
                  print('Bucket ' + bucket_name + ' already exists')
            except minio.error.BucketAlreadyExists:
              pass
            except minio.error.BucketAlreadyOwnedByYou:
              pass
              
        def is_file_existed(self,bucket_name,file_path):
            try:
                stat = self.minio_client.stat_object(storage_bucket, file_path)
                print(os.path.join(bucket_name,stat.object_name) + ' exists')
                return True
            except Exception as err:
                print(os.path.join(bucket_name,file_path) + ' does not exist')
                return False
                
        def upload_from_path(self,bucket_name,local_path,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(local_path,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(local_path,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(local_path,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(local_path,file_path)))
                    else:
                        if sub_folder == None:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path))
                        else:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path),sub_folder)
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,local_path,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + local_path)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,local_path),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,local_path))
          
        def upload_from_path_and_rename(self,bucket_name,local_path,new_name,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(new_name,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(new_name,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(new_name,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(new_name,file_path)))                    
                    else:
                        if sub_folder == None:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path))
                        else:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path),sub_folder)
                        
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,new_name,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + new_name)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,new_name),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,new_name))
                    
        def download_from_path(self,bucket_name,remote_path,local_path=None):
            dest_path = ''
            if local_path == None:
                dest_path = os.getcwd()
            else:
                dest_path = local_path
                
            print(os.path.join(dest_path,remote_path))
            if not os.path.isdir(os.path.join(dest_path,remote_path)):
                os.makedirs(os.path.join(dest_path,remote_path), exist_ok=True)
                print('made dir ' + remote_path)
            objects = storage_client.minio_client.list_objects(bucket_name, prefix=remote_path,recursive=True)
            for obj in objects:
                self.download_file_path(bucket_name, obj.object_name, os.path.join(dest_path,obj.object_name))  
                print('Downloaded from ' + os.path.join(bucket_name,obj.object_name) + ' to ' + os.path.join(dest_path,obj.object_name))
        
        def upload_file_path(self,bucket_name,file_path,local_path,sub_folder=None):
            if sub_folder == None:
                self.minio_client.fput_object(bucket_name,file_path,local_path)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from ' + local_path)
            else:
                self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,file_path),local_path)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from ' + local_path)
          
        def download_file_path(self,bucket_name,file_path,local_path):
            self.minio_client.fget_object(bucket_name,file_path,local_path)
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to ' + local_path)        
            
        def upload_file(self,bucket_name,file_path,data,length,sub_folder=None):
            if sub_folder == None:
                self.minio_client.put_object(bucket_name, file_path, data, length)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from buffer')
            else:
                self.minio_client.put_object(bucket_name, os.path.join(sub_folder,file_path), data, length)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from buffer')
            
          
        def download_file(self,bucket_name,file_path):
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to buffer')
            return self.minio_client.get_object(bucket_name, file_path)
            
        def upload_folder_from_sftp(self,pipeline_client,sftp_folder_parent_path,sftp_folder_name,bucket_name,file_path,sub_folder=None):
            item_list = pipeline_client.sftp.listdir_attr(os.path.join(sftp_folder_parent_path,sftp_folder_name))
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    print('dir ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    self.upload_folder_from_sftp(pipeline_client,os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename,bucket_name,os.path.join(file_path,item.filename))
                else:
                    print('file ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    with pipeline_client.sftp.open(os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename), "rb") as fl:
                        fl.prefetch()
                        if sub_folder == None:
                            self.upload_file(bucket_name, os.path.join(file_path,item.filename), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(file_path,item.filename))
                        else:
                            self.upload_file(bucket_name, os.path.join(sub_folder,os.path.join(file_path,item.filename)), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(file_path,item.filename)))
                    
        def transfer_folder_to_sftp(self,pipeline_client,bucket_name,folder,remote_parent_path):
            objects = self.minio_client.list_objects(bucket_name, prefix=folder)
            for obj in objects:
                if obj.is_dir:
                    print('dir ',os.path.join(bucket_name,obj.object_name),os.path.join(remote_parent_path,obj.object_name))
                    if not pipeline_client.is_dir_path_existed_remotely(os.path.join(remote_parent_path,obj.object_name)):
                        pipeline_client.mkdir_nested_remotely(os.path.join(remote_parent_path,obj.object_name))                
                    print(os.path.join(bucket_name,obj.object_name) + ' is dir')
                    self.transfer_folder_to_sftp(pipeline_client,bucket_name,obj.object_name,remote_parent_path)
                else:
                    print('file ',bucket_name + '/' + obj.object_name,os.path.join(remote_parent_path,obj.object_name))
                    file = self.download_file(bucket_name, obj.object_name)
                    pipeline_client.sftp.putfo(file, os.path.join(remote_parent_path,obj.object_name))
                    print('Transferred from ' + bucket_name + '/' + obj.object_name + ' to ' + os.path.join(remote_parent_path,obj.object_name))
                    
        def upload_file_from_sftp(self,pipeline_client,sftp_file_path,bucket_name,sub_folder=None):
            with pipeline_client.sftp.open(sftp_file_path, "rb") as fl:
                fl.prefetch()
                if sub_folder == None:
                    self.upload_file(bucket_name, sftp_file_path.split('/')[-1], fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + bucket_name + '/' + sftp_file_path.split('/')[-1])  
                else:
                    self.upload_file(bucket_name, os.path.join(sub_folder,sftp_file_path.split('/')[-1]), fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + os.path.join(bucket_name,os.path.join(sub_folder,sftp_file_path.split('/')[-1])))          
                    
        def transfer_file_to_sftp(self,pipeline_client,bucket_name,file_path,remote_path):
            file = self.download_file(bucket_name, file_path)
            pipeline_client.sftp.putfo(file, remote_path)
            print('Transferred from ' + bucket_name + '/' + remote_path + ' to ' + remote_path)
    
    def add_array_to_array(array,project_name,sim_name,array_to_add,array_key=None):
        project_keys = []
        for project in array:
            for project_key in project.keys():
                project_keys.append(project_key)
                
        if array_key == None:
            if project_name in project_keys:
                for project in array:
                    if project_name in project.keys():
                        project[project_name].append({sim_name : array_to_add})
            else:
                array.append({project_name : [{sim_name : array_to_add}]})
        else:
            # print('Input: ',array_key,project_name,sim_name, project_keys)
            if project_name not in project_keys:
                # print(project_name + ' not available, adding')
                array.append({project_name : [{sim_name : {array_key : array_to_add}}]})
            else:
                for project in array:
                    # print(' Checking ' + project_name)
                    if project_name in project.keys():
                        sim_keys = []
                        for simulation in project[project_name]:
                            for sim_key in simulation.keys():
                                sim_keys.append(sim_key)
                                
                        if sim_name not in sim_keys: 
                            # print('   ' + sim_name + ' not in project, adding')
                            project[project_name].append({sim_name : {array_key : array_to_add}})
                            break
                        else:
                            # print(project_name,sim_keys)                            
                            for simulation in project[project_name]:
                                # print('  Checking ' + project_name + ' ' + sim_name)                        
                                if sim_name in simulation.keys():
                                    # print('   ' + sim_name + ' in project')
                                    if array_key in simulation[sim_name].keys():
                                        # print('    Array ' + array_key + ' in ' + sim_name)
                                        for item in array_to_add:
                                            simulation[sim_name][array_key].append(item)
                                    else:
                                        # print('    Array ' + str(array_key + ' not in ' + sim_name) + ' adding')
                                        simulation[sim_name][array_key] = array_to_add
                                        break
                                    
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
    
    downloaded_files_and_dirs = []   
    generated_files_and_dirs = [] 
    new_dirs_and_files = []
    download_folder = ''
    #Download file to local or remote
    for project_index,project in enumerate(remote_files):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                before_dirs_and_files = [f for f in os.listdir()]
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for field in simulation[sim_name].keys():
                        if field == 'task':
                            for files in simulation[sim_name][field]:
                                for working_path in files.keys():
                                    if working_path == 'None':                            
                                        download_folder = project_name + '_' + sim_name + '_' + remote_sim['work_dirs']['script']
                                        cmd_wget_local = 'mkdir -p ' + download_folder + ' && wget ' + files[working_path] + ' -P ' + download_folder + ' -N'
                                        print(project_name + ': ' + field + ': ' + cmd_wget_local)
                                        subprocess.call(cmd_wget_local,shell=True)
                                    else:
                                        print(project_name + ': ' + field + ': wget ' + files[working_path] + ' -P ' + working_path + ' -N')
                                        pipeline_client.run_cmd_remotely('wget ' + files[working_path] + ' -P ' + working_path + ' -N')
                after_dirs_and_files = [f for f in os.listdir()]
                new_dirs_and_files = []
                for item in after_dirs_and_files:
                    if item not in before_dirs_and_files:
                        new_dirs_and_files.append(item)
                print(new_dirs_and_files)
                if len(new_dirs_and_files) > 0:
                    add_array_to_array(downloaded_files_and_dirs, project_name, sim_name, new_dirs_and_files)
            
    subprocess.call('ls -lh',shell=True) 
        
    print(downloaded_files_and_dirs)
                 
    remote_cmd_to_run = []                
    for project_index,project in enumerate(remote_tasks):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                sim_cmd_to_run = []
                before_dirs_and_files = [f for f in os.listdir()]
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for tasks in simulation[sim_name]:
                        for task_path in tasks.keys():
                            for script_name in tasks[task_path].keys():
                                print(project_name + ': sim ' + sim_name + ': task ' + script_name + ': cd ' + task_path + ' && run ' + tasks[task_path][script_name])
                                if task_path =='None':
                                    cmd_run_local = 'cd ' + download_folder + ' && ' + tasks[task_path][script_name]
                                    subprocess.call(cmd_run_local, shell=True)
                                else:
                                    cmd_run_remote = 'cd ' + task_path + ' && ' + tasks[task_path][script_name]
                                    sim_cmd_to_run.append(cmd_run_remote)
                after_dirs_and_files = [f for f in os.listdir()]
                new_dirs_and_files = []
                for item in after_dirs_and_files:
                    if item not in before_dirs_and_files:
                        new_dirs_and_files.append(item)
                print(new_dirs_and_files)
                if len(new_dirs_and_files) > 0:
                    add_array_to_array(generated_files_and_dirs, project_name, sim_name, new_dirs_and_files)
                add_array_to_array(remote_cmd_to_run, project_name, sim_name, sim_cmd_to_run)
            
    for project_index,project in enumerate(downloaded_files_and_dirs):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    if len(simulation[sim_name]) > 0:
                        print('Checking local downloaded folder')
                        if remote_sim['using_storage'] == 'True':
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path(storage_bucket, item_tar_path,sim_name)              
                            else:
                                print('Sync folders to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_and_delete_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path_and_rename(storage_bucket, item_tar_path,sim_name)
                        else:
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote')
                                for item in simulation[sim_name]:                                    
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                            else:
                                print('Sync folders remote')
                                for item in simulation[sim_name]:
                                    item_path_remote = item.split('_')[-1]
                                    pipeline_client.upload_from_path(item, remote_sim['work_path'],item_path_remote)   
    
    subprocess.call('ls -lh',shell=True)
                                
    print(generated_files_and_dirs)
                                
    for project_index,project in enumerate(generated_files_and_dirs):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    if len(simulation[sim_name]) > 0:
                        print('Checking local generated folder')
                        if remote_sim['using_storage'] == 'True':
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path(storage_bucket, item_tar_path,sim_name)              
                            else:
                                print('Sync folders to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_and_delete_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path_and_rename(storage_bucket, item_tar_path,sim_name)
                        else:
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote')
                                for item in simulation[sim_name]:                                    
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                            else:
                                print('Sync folders remote')
                                for item in simulation[sim_name]:
                                    item_path_remote = item.split('_')[-1]
                                    pipeline_client.upload_from_path(item, remote_sim['work_path'],item_path_remote)
                            
                                
    for project_index,project in enumerate(remote_cmd_to_run):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for remote_cmd in simulation[sim_name]:
                        pipeline_client.run_cmd_remotely(remote_cmd)
                        
    #Working with folders on remote
    for project_index,project in enumerate(remote_storages):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    print('Checking remote generated folder')
                    if remote_sim['using_storage'] == 'True':
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote and storage')
                            for item in [remote_sim['work_dirs']['input'],remote_sim['work_dirs']['script']]:
                                item_tar_path = item + '.tar.gz'
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item)
                                storage_client.upload_file_from_sftp(pipeline_client, os.path.join(remote_sim['work_path'], item_tar_path),storage_bucket,sim_name)       
                        else:
                            print('Sync folders to remote and storage')
                            for item in [remote_sim['work_dirs']['input'],remote_sim['work_dirs']['script']]:
                                storage_client.upload_folder_from_sftp(pipeline_client, remote_sim['work_path'],item,storage_bucket,item,sim_name)
                    else:
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote')
                            for item in [remote_sim['work_dirs']['input'],remote_sim['work_dirs']['script']]:
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item) 
                        else:
                            print('Not using tar or storage')
                
    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])    
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)

def step_5_save_outputs(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import tarfile
    import os.path
    import subprocess
    import json 
    import threading
    import time
    from stat import S_ISDIR, S_ISREG 
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close() 
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                    
         
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
       
    import minio
    from minio import Minio
    import re
    import time
    class StorageClient():
        minio_client = 0 
       
        def connect(self,host='host:port',
                  username='key',
                  password='secret'):
            self.minio_client = Minio(endpoint=host,
                    access_key=username,
                    secret_key=password,
                    secure=False)
          
        def make_bucket(self,bucket_name):
            try:
              found = self.minio_client.bucket_exists(bucket_name)
              if not found:
                  self.minio_client.make_bucket(bucket_name)
              else:
                  print('Bucket ' + bucket_name + ' already exists')
            except minio.error.BucketAlreadyExists:
              pass
            except minio.error.BucketAlreadyOwnedByYou:
              pass
              
        def is_file_existed(self,bucket_name,file_path):
            try:
                stat = self.minio_client.stat_object(storage_bucket, file_path)
                print(os.path.join(bucket_name,stat.object_name) + ' exists')
                return True
            except Exception as err:
                print(os.path.join(bucket_name,file_path) + ' does not exist')
                return False
                
        def upload_from_path(self,bucket_name,local_path,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(local_path,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(local_path,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(local_path,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(local_path,file_path)))
                    else:
                        if sub_folder == None:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path))
                        else:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path),sub_folder)
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,local_path,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + local_path)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,local_path),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,local_path))
          
        def upload_from_path_and_rename(self,bucket_name,local_path,new_name,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(new_name,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(new_name,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(new_name,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(new_name,file_path)))                    
                    else:
                        if sub_folder == None:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path))
                        else:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path),sub_folder)
                        
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,new_name,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + new_name)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,new_name),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,new_name))
                    
        def download_from_path(self,bucket_name,remote_path,local_path=None):
            dest_path = ''
            if local_path == None:
                dest_path = os.getcwd()
            else:
                dest_path = local_path
                
            print(os.path.join(dest_path,remote_path))
            if not os.path.isdir(os.path.join(dest_path,remote_path)):
                os.makedirs(os.path.join(dest_path,remote_path), exist_ok=True)
                print('made dir ' + remote_path)
            objects = storage_client.minio_client.list_objects(bucket_name, prefix=remote_path,recursive=True)
            for obj in objects:
                self.download_file_path(bucket_name, obj.object_name, os.path.join(dest_path,obj.object_name))  
                print('Downloaded from ' + os.path.join(bucket_name,obj.object_name) + ' to ' + os.path.join(dest_path,obj.object_name))
        
        def upload_file_path(self,bucket_name,file_path,local_path,sub_folder=None):
            if sub_folder == None:
                self.minio_client.fput_object(bucket_name,file_path,local_path)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from ' + local_path)
            else:
                self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,file_path),local_path)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from ' + local_path)
          
        def download_file_path(self,bucket_name,file_path,local_path):
            self.minio_client.fget_object(bucket_name,file_path,local_path)
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to ' + local_path)        
            
        def upload_file(self,bucket_name,file_path,data,length,sub_folder=None):
            if sub_folder == None:
                self.minio_client.put_object(bucket_name, file_path, data, length)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from buffer')
            else:
                self.minio_client.put_object(bucket_name, os.path.join(sub_folder,file_path), data, length)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from buffer')
            
          
        def download_file(self,bucket_name,file_path):
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to buffer')
            return self.minio_client.get_object(bucket_name, file_path)
            
        def upload_folder_from_sftp(self,pipeline_client,sftp_folder_parent_path,sftp_folder_name,bucket_name,file_path,sub_folder=None):
            item_list = pipeline_client.sftp.listdir_attr(os.path.join(sftp_folder_parent_path,sftp_folder_name))
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    print('dir ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    self.upload_folder_from_sftp(pipeline_client,os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename,bucket_name,os.path.join(file_path,item.filename))
                else:
                    print('file ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    with pipeline_client.sftp.open(os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename), "rb") as fl:
                        fl.prefetch()
                        if sub_folder == None:
                            self.upload_file(bucket_name, os.path.join(file_path,item.filename), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(file_path,item.filename))
                        else:
                            self.upload_file(bucket_name, os.path.join(sub_folder,os.path.join(file_path,item.filename)), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(file_path,item.filename)))
                    
        def transfer_folder_to_sftp(self,pipeline_client,bucket_name,folder,remote_parent_path):
            objects = self.minio_client.list_objects(bucket_name, prefix=folder)
            for obj in objects:
                if obj.is_dir:
                    print('dir ',os.path.join(bucket_name,obj.object_name),os.path.join(remote_parent_path,obj.object_name))
                    if not pipeline_client.is_dir_path_existed_remotely(os.path.join(remote_parent_path,obj.object_name)):
                        pipeline_client.mkdir_nested_remotely(os.path.join(remote_parent_path,obj.object_name))                
                    print(os.path.join(bucket_name,obj.object_name) + ' is dir')
                    self.transfer_folder_to_sftp(pipeline_client,bucket_name,obj.object_name,remote_parent_path)
                else:
                    print('file ',bucket_name + '/' + obj.object_name,os.path.join(remote_parent_path,obj.object_name))
                    file = self.download_file(bucket_name, obj.object_name)
                    pipeline_client.sftp.putfo(file, os.path.join(remote_parent_path,obj.object_name))
                    print('Transferred from ' + bucket_name + '/' + obj.object_name + ' to ' + os.path.join(remote_parent_path,obj.object_name))
                    
        def upload_file_from_sftp(self,pipeline_client,sftp_file_path,bucket_name,sub_folder=None):
            with pipeline_client.sftp.open(sftp_file_path, "rb") as fl:
                fl.prefetch()
                if sub_folder == None:
                    self.upload_file(bucket_name, sftp_file_path.split('/')[-1], fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + bucket_name + '/' + sftp_file_path.split('/')[-1])  
                else:
                    self.upload_file(bucket_name, os.path.join(sub_folder,sftp_file_path.split('/')[-1]), fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + os.path.join(bucket_name,os.path.join(sub_folder,sftp_file_path.split('/')[-1])))          
                    
        def transfer_file_to_sftp(self,pipeline_client,bucket_name,file_path,remote_path):
            file = self.download_file(bucket_name, file_path)
            pipeline_client.sftp.putfo(file, remote_path)
            print('Transferred from ' + bucket_name + '/' + remote_path + ' to ' + remote_path)
    
    def check_qstat(pipeline_client,project_name,remote_auth_username,remote_work_name,check_interval):
        print('Waiting for ' + project_name + ' to finish running')
        while True:
           job_status = pipeline_client.get_run_cmd_remotely('qstat -u ' + remote_auth_username + ' | grep ' + remote_work_name)
           if job_status == []:
              print(project_name + ' finished running')          
              break
           for line in job_status:
              print(line.rstrip())
           job_status = []
           time.sleep(int(check_interval))
               
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
    
    remote_auth_username = remote_auth['ssh_username']
    for project_index,project in enumerate(remote_sims):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    job_name = project_name + '_' + sim_name
                    if len(job_name) >= 16:
                        job_name = project_name[0:7] + '_' + sim_name[-7:]
                    check_interval = simulation[sim_name]['check_interval']
                    thread = threading.Thread(target=check_qstat(pipeline_client,project_name, remote_auth_username, job_name, check_interval))
                    thread.start()
        
    #Working with output on remote
    for project_index,project in enumerate(remote_sims):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = simulation[sim_name]
                    print('Checking remote generated folder')
                    if remote_sim['using_storage'] == 'True':
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote and storage')
                            for item in [remote_sim['work_dirs']['output']]:
                                item_tar_path = item + '.tar.gz'
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item)
                                storage_client.upload_file_from_sftp(pipeline_client, os.path.join(remote_sim['work_path'], item_tar_path),storage_bucket,sim_name)       
                        else:
                            print('Sync folders to remote and storage')
                            for item in [remote_sim['work_dirs']['output']]:
                                storage_client.upload_folder_from_sftp(pipeline_client, remote_sim['work_path'],item,storage_bucket,item,sim_name)
                    else:
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote')
                            for item in [remote_sim['work_dirs']['output']]:
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item) 
                        else:
                            print('Not using tar or storage')
        
    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])    
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)

def step_6_run_plots(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import tarfile
    import os.path
    import subprocess
    import json
    from stat import S_ISDIR, S_ISREG 
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close()
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                    
         
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
       
    import minio
    from minio import Minio
    import re
    import time
    class StorageClient():
        minio_client = 0 
       
        def connect(self,host='host:port',
                  username='key',
                  password='secret'):
            self.minio_client = Minio(endpoint=host,
                    access_key=username,
                    secret_key=password,
                    secure=False)
          
        def make_bucket(self,bucket_name):
            try:
              found = self.minio_client.bucket_exists(bucket_name)
              if not found:
                  self.minio_client.make_bucket(bucket_name)
              else:
                  print('Bucket ' + bucket_name + ' already exists')
            except minio.error.BucketAlreadyExists:
              pass
            except minio.error.BucketAlreadyOwnedByYou:
              pass
              
        def is_file_existed(self,bucket_name,file_path):
            try:
                stat = self.minio_client.stat_object(storage_bucket, file_path)
                print(os.path.join(bucket_name,stat.object_name) + ' exists')
                return True
            except Exception as err:
                print(os.path.join(bucket_name,file_path) + ' does not exist')
                return False
                
        def upload_from_path(self,bucket_name,local_path,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(local_path,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(local_path,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(local_path,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(local_path,file_path)))
                    else:
                        if sub_folder == None:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path))
                        else:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path),sub_folder)
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,local_path,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + local_path)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,local_path),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,local_path))
          
        def upload_from_path_and_rename(self,bucket_name,local_path,new_name,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(new_name,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(new_name,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(new_name,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(new_name,file_path)))                    
                    else:
                        if sub_folder == None:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path))
                        else:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path),sub_folder)
                        
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,new_name,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + new_name)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,new_name),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,new_name))
                    
        def download_from_path(self,bucket_name,remote_path,local_path=None):
            dest_path = ''
            if local_path == None:
                dest_path = os.getcwd()
            else:
                dest_path = local_path
                
            print(os.path.join(dest_path,remote_path))
            if not os.path.isdir(os.path.join(dest_path,remote_path)):
                os.makedirs(os.path.join(dest_path,remote_path), exist_ok=True)
                print('made dir ' + remote_path)
            objects = storage_client.minio_client.list_objects(bucket_name, prefix=remote_path,recursive=True)
            for obj in objects:
                self.download_file_path(bucket_name, obj.object_name, os.path.join(dest_path,obj.object_name))  
                print('Downloaded from ' + os.path.join(bucket_name,obj.object_name) + ' to ' + os.path.join(dest_path,obj.object_name))
        
        def upload_file_path(self,bucket_name,file_path,local_path,sub_folder=None):
            if sub_folder == None:
                self.minio_client.fput_object(bucket_name,file_path,local_path)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from ' + local_path)
            else:
                self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,file_path),local_path)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from ' + local_path)
          
        def download_file_path(self,bucket_name,file_path,local_path):
            self.minio_client.fget_object(bucket_name,file_path,local_path)
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to ' + local_path)        
            
        def upload_file(self,bucket_name,file_path,data,length,sub_folder=None):
            if sub_folder == None:
                self.minio_client.put_object(bucket_name, file_path, data, length)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from buffer')
            else:
                self.minio_client.put_object(bucket_name, os.path.join(sub_folder,file_path), data, length)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from buffer')
            
          
        def download_file(self,bucket_name,file_path):
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to buffer')
            return self.minio_client.get_object(bucket_name, file_path)
            
        def upload_folder_from_sftp(self,pipeline_client,sftp_folder_parent_path,sftp_folder_name,bucket_name,file_path,sub_folder=None):
            item_list = pipeline_client.sftp.listdir_attr(os.path.join(sftp_folder_parent_path,sftp_folder_name))
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    print('dir ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    self.upload_folder_from_sftp(pipeline_client,os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename,bucket_name,os.path.join(file_path,item.filename))
                else:
                    print('file ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    with pipeline_client.sftp.open(os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename), "rb") as fl:
                        fl.prefetch()
                        if sub_folder == None:
                            self.upload_file(bucket_name, os.path.join(file_path,item.filename), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(file_path,item.filename))
                        else:
                            self.upload_file(bucket_name, os.path.join(sub_folder,os.path.join(file_path,item.filename)), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(file_path,item.filename)))
                    
        def transfer_folder_to_sftp(self,pipeline_client,bucket_name,folder,remote_parent_path):
            objects = self.minio_client.list_objects(bucket_name, prefix=folder)
            for obj in objects:
                if obj.is_dir:
                    print('dir ',os.path.join(bucket_name,obj.object_name),os.path.join(remote_parent_path,obj.object_name))
                    if not pipeline_client.is_dir_path_existed_remotely(os.path.join(remote_parent_path,obj.object_name)):
                        pipeline_client.mkdir_nested_remotely(os.path.join(remote_parent_path,obj.object_name))                
                    print(os.path.join(bucket_name,obj.object_name) + ' is dir')
                    self.transfer_folder_to_sftp(pipeline_client,bucket_name,obj.object_name,remote_parent_path)
                else:
                    print('file ',bucket_name + '/' + obj.object_name,os.path.join(remote_parent_path,obj.object_name))
                    file = self.download_file(bucket_name, obj.object_name)
                    pipeline_client.sftp.putfo(file, os.path.join(remote_parent_path,obj.object_name))
                    print('Transferred from ' + bucket_name + '/' + obj.object_name + ' to ' + os.path.join(remote_parent_path,obj.object_name))
                    
        def upload_file_from_sftp(self,pipeline_client,sftp_file_path,bucket_name,sub_folder=None):
            with pipeline_client.sftp.open(sftp_file_path, "rb") as fl:
                fl.prefetch()
                if sub_folder == None:
                    self.upload_file(bucket_name, sftp_file_path.split('/')[-1], fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + bucket_name + '/' + sftp_file_path.split('/')[-1])  
                else:
                    self.upload_file(bucket_name, os.path.join(sub_folder,sftp_file_path.split('/')[-1]), fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + os.path.join(bucket_name,os.path.join(sub_folder,sftp_file_path.split('/')[-1])))          
                    
        def transfer_file_to_sftp(self,pipeline_client,bucket_name,file_path,remote_path):
            file = self.download_file(bucket_name, file_path)
            pipeline_client.sftp.putfo(file, remote_path)
            print('Transferred from ' + bucket_name + '/' + remote_path + ' to ' + remote_path)
            
    def add_array_to_array(array,project_name,sim_name,array_to_add,array_key=None):
        project_keys = []
        for project in array:
            for project_key in project.keys():
                project_keys.append(project_key)
                
        if array_key == None:
            if project_name in project_keys:
                for project in array:
                    if project_name in project.keys():
                        project[project_name].append({sim_name : array_to_add})
            else:
                array.append({project_name : [{sim_name : array_to_add}]})
        else:
            # print('Input: ',array_key,project_name,sim_name, project_keys)
            if project_name not in project_keys:
                # print(project_name + ' not available, adding')
                array.append({project_name : [{sim_name : {array_key : array_to_add}}]})
            else:
                for project in array:
                    # print(' Checking ' + project_name)
                    if project_name in project.keys():
                        sim_keys = []
                        for simulation in project[project_name]:
                            for sim_key in simulation.keys():
                                sim_keys.append(sim_key)
                                
                        if sim_name not in sim_keys: 
                            # print('   ' + sim_name + ' not in project, adding')
                            project[project_name].append({sim_name : {array_key : array_to_add}})
                            break
                        else:
                            # print(project_name,sim_keys)                            
                            for simulation in project[project_name]:
                                # print('  Checking ' + project_name + ' ' + sim_name)                        
                                if sim_name in simulation.keys():
                                    # print('   ' + sim_name + ' in project')
                                    if array_key in simulation[sim_name].keys():
                                        # print('    Array ' + array_key + ' in ' + sim_name)
                                        for item in array_to_add:
                                            simulation[sim_name][array_key].append(item)
                                    else:
                                        # print('    Array ' + str(array_key + ' not in ' + sim_name) + ' adding')
                                        simulation[sim_name][array_key] = array_to_add
                                        break
                                    
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
              
    downloaded_files_and_dirs = []   
    generated_files_and_dirs = [] 
    new_dirs_and_files = []
    download_folder = ''
    #Download file to local or remote
    for project_index,project in enumerate(remote_files):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                before_dirs_and_files = [f for f in os.listdir()]
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for field in simulation[sim_name].keys():
                        if field == 'plot':
                            for files in simulation[sim_name][field]:
                                for working_path in files.keys():
                                    if working_path == 'None':  
                                        download_folder = project_name + '_' + sim_name + '_' + remote_sim['work_dirs']['plot']
                                        cmd_wget_local = 'mkdir -p ' + download_folder + ' && wget ' + files[working_path] + ' -P ' + download_folder + ' -N'
                                        print(project_name + ': ' + field + ': ' + cmd_wget_local)
                                        subprocess.call(cmd_wget_local,shell=True)
                                    else:
                                        print(project_name + ': ' + field + ': wget ' + files[working_path] + ' -P ' + working_path + ' -N')
                                        pipeline_client.run_cmd_remotely('wget ' + files[working_path] + ' -P ' + working_path + ' -N')
                after_dirs_and_files = [f for f in os.listdir()]
                new_dirs_and_files = []
                for item in after_dirs_and_files:
                    if item not in before_dirs_and_files:
                        new_dirs_and_files.append(item)
                print(new_dirs_and_files)
                if len(new_dirs_and_files) > 0:
                    add_array_to_array(downloaded_files_and_dirs, project_name, sim_name, new_dirs_and_files)
            
    subprocess.call('ls -lh',shell=True) 
        
    print(downloaded_files_and_dirs)
                 
    remote_cmd_to_run = []                
    for project_index,project in enumerate(remote_plots):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                sim_cmd_to_run = []
                before_dirs_and_files = [f for f in os.listdir()]
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for plots in simulation[sim_name]:
                        for plot_path in plots.keys():
                            for figure_name in plots[plot_path].keys():
                                print(project_name + ': sim ' + sim_name + ': figure ' + figure_name + ': cd ' + plot_path + ' && run ' + plots[plot_path][figure_name])
                                if plot_path =='None':
                                    cmd_run_local = 'cd ' + download_folder + ' && ' + plots[plot_path][figure_name]
                                    subprocess.call(cmd_run_local, shell=True)
                                else:
                                    cmd_run_remote = 'cd ' + plot_path + ' && ' + plots[plot_path][figure_name]
                                    sim_cmd_to_run.append(cmd_run_remote)
                after_dirs_and_files = [f for f in os.listdir()]
                new_dirs_and_files = []
                for item in after_dirs_and_files:
                    if item not in before_dirs_and_files:
                        new_dirs_and_files.append(item)
                print(new_dirs_and_files)
                if len(new_dirs_and_files) > 0:
                    add_array_to_array(generated_files_and_dirs, project_name, sim_name, new_dirs_and_files)
                add_array_to_array(remote_cmd_to_run, project_name, sim_name, sim_cmd_to_run)
            
    for project_index,project in enumerate(downloaded_files_and_dirs):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    if len(simulation[sim_name]) > 0:
                        print('Checking local downloaded folder')
                        if remote_sim['using_storage'] == 'True':
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path(storage_bucket, item_tar_path,sim_name)              
                            else:
                                print('Sync folders to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_and_delete_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path_and_rename(storage_bucket, item_tar_path,sim_name)
                        else:
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote')
                                for item in simulation[sim_name]:                                    
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                            else:
                                print('Sync folders remote')
                                for item in simulation[sim_name]:
                                    item_path_remote = item.split('_')[-1]
                                    pipeline_client.upload_from_path(item, remote_sim['work_path'],item_path_remote)   
    
    subprocess.call('ls -lh',shell=True)
                                
    print(generated_files_and_dirs)
                                
    for project_index,project in enumerate(generated_files_and_dirs):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    if len(simulation[sim_name]) > 0:
                        print('Checking local generated folder')
                        if remote_sim['using_storage'] == 'True':
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path(storage_bucket, item_tar_path,sim_name)              
                            else:
                                print('Sync folders to remote and storage')
                                for item in simulation[sim_name]:
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_and_delete_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                                    storage_client.upload_from_path_and_rename(storage_bucket, item_tar_path,sim_name)
                        else:
                            if remote_sim['using_tar'] == 'True':
                                print('Sync tar files to remote')
                                for item in simulation[sim_name]:                                    
                                    item_tar_path = item.split('_')[-1] + '.tar.gz'
                                    pipeline_client.compress_file_path(item_tar_path, item)
                                    pipeline_client.upload_from_path(item_tar_path, remote_sim['work_path'])
                                    pipeline_client.uncompress_tar_file_remotely(remote_sim['work_path'],item_tar_path,item.split('_')[-1])
                            else:
                                print('Sync folders remote')
                                for item in simulation[sim_name]:
                                    item_path_remote = item.split('_')[-1]
                                    pipeline_client.upload_from_path(item, remote_sim['work_path'],item_path_remote)
                                
    for project_index,project in enumerate(remote_cmd_to_run):
        for project_name in project.keys():
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    for remote_cmd in simulation[sim_name]:
                        pipeline_client.run_cmd_remotely(remote_cmd)
                        
    #Working with folders on remote
    for project_index,project in enumerate(remote_storages):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    print('Checking remote generated folder')
                    if remote_sim['using_storage'] == 'True':
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote and storage')
                            for item in [remote_sim['work_dirs']['plot']]:
                                item_tar_path = item + '.tar.gz'
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item)
                                storage_client.upload_file_from_sftp(pipeline_client, os.path.join(remote_sim['work_path'], item_tar_path),storage_bucket,sim_name)       
                        else:
                            print('Sync folders to remote and storage')
                            for item in [remote_sim['work_dirs']['plot']]:
                                storage_client.upload_folder_from_sftp(pipeline_client, remote_sim['work_path'],item,storage_bucket,item,sim_name)
                    else:
                        if remote_sim['using_tar'] == 'True':
                            print('Sync tar files to remote')
                            for item in [remote_sim['work_dirs']['plot']]:
                                pipeline_client.compress_file_path_remotely(remote_sim['work_path'], item) 
                        else:
                            print('Not using tar or storage')
      
    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])    
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)

def step_7_download_data(remote_auth: dict,
                        remote_repo: list,
                        remote_sims: list,
                        remote_binaries: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_storages: list,
                        remote_tasks: list,
                        remote_plots: list) -> NamedTuple('outputs', [
                        ('remote_auth', dict),
                        ('remote_repo', list),
                        ('remote_sims', list),
                        ('remote_binaries', list),
                        ('remote_dirs', list),
                        ('remote_files', list),
                        ('remote_storages', list),
                        ('remote_tasks', list),
                        ('remote_plots', list)
                        ]):
    from collections import namedtuple
    import paramiko
    import os
    import io
    from collections import namedtuple
    from io import StringIO
    import sys
    import tarfile
    import os.path
    import subprocess
    import json
    from stat import S_ISDIR, S_ISREG 
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0

        def disconnect(self):            
            self.ssh.close()
            self.sftp.close()

        def run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            for line in stdout.readlines():
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               print(err)

        def get_run_cmd_remotely(self, command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command, get_pty=True)
            lines = []
            for line in stdout.readlines():
               lines.append(line)
               print(line.rstrip())
            err = stderr.read().decode()
            if err:
               lines.append(line)
               print(err)
            return lines

        def is_dir_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.chdir(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def is_file_path_existed_remotely(self, file_path):
            is_existed = False
            try:
               self.sftp.stat(file_path)  # sub-directory exists
               print(file_path + ' exists')
               is_existed = True
            except IOError:
               print(file_path + ' does not exist')
            return is_existed

        def mkdir_nested_remotely(self, remote_directory):
            """Change to this directory, recursively making new folders if needed.
            Returns True if any folders were created."""
            if remote_directory == '/':
               # absolute path so change directory to root
               self.sftp.chdir('/')
               return
            if remote_directory == '':
               # top-level relative directory must exist
               return
            try:
               self.sftp.chdir(remote_directory)  # sub-directory exists
            except IOError:
               dirname, basename = os.path.split(remote_directory.rstrip('/'))
               self.mkdir_nested_remotely(dirname)  # make parent directories
               self.sftp.mkdir(basename)  # sub-directory missing, so created it
               self.sftp.chdir(basename)
               return True
        
        def compress_file_path_remotely(self,remote_parent_path,source_path,tar_name=None):
            if tar_name == None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + source_path.split('/')[-1] + '.tar.gz' + ' ' + source_path)
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar cvf ' + tar_name + '.tar.gz' + ' ' + source_path)
                
        def uncompress_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
                    
        def uncompress_and_delete_tar_file_remotely(self,remote_parent_path,tar_file,output_path=None):
            if output_path != None:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file + ' -C ' + output_path + ' --strip-components=1')
            else:
                self.run_cmd_remotely('cd ' + remote_parent_path + ' && tar xvf ' + tar_file)
            self.run_cmd_remotely('cd ' + remote_parent_path + ' && rm ' + tar_file)
        
        def compress_file_path(self,tar_name, source_path):
            with tarfile.open(tar_name, "w:gz") as tar:
                tar.add(source_path, arcname=os.path.basename(source_path), recursive=True)
            tar.close()
                
        def uncompress_tar_file(self,tar_path,member=None,dest_path=None):
            tar = tarfile.open(tar_path)        
            if dest_path == None:
                if member == None:
                    tar.extractall()
                else:
                    tar.extractall(member)
            else:
                if member == None:
                    tar.extractall(dest_path)
                else:
                    tar.extractall(member,dest_path)            
            tar.close()
                
        def upload_from_path(self,local_path,remote_parent_path,remote_path=None):
            if remote_path == None:
                dest_path = local_path
            else:
                dest_path = remote_path
            if os.path.isdir(local_path):                        
                self.mkdir_nested_remotely(os.path.join(remote_parent_path,dest_path))
                print('mkdir remote ' + os.path.join(remote_parent_path,dest_path))    
                for file_path in os.listdir(local_path):
                    if os.path.isdir(os.path.join(local_path,file_path)):
                        print('dir ',os.path.join(local_path,file_path))
                        self.upload_from_path(os.path.join(local_path,file_path),remote_parent_path,os.path.join(dest_path,file_path))
                    else:
                        print('file ',os.path.join(local_path,file_path))
                        self.sftp.put(os.path.join(local_path,file_path), os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
                        print('upload ' + os.path.join(local_path,file_path) + ' to ' + os.path.join(remote_parent_path,os.path.join(dest_path,file_path)))
            else:
                self.sftp.put(local_path, os.path.join(remote_parent_path,dest_path))
                print('upload ' + local_path + ' to ' + os.path.join(remote_parent_path,dest_path))                    
         
        def download_from_path(self,remote_path, local_path=None):
            print('Downloading ' + remote_path)
            fileattr = self.sftp.lstat(remote_path)
            if S_ISDIR(fileattr.st_mode):
                print('is Directory')
                item_list = self.sftp.listdir_attr(remote_path)
                if local_path != None:
                    if not os.path.isdir(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            self.download_from_path(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),os.path.join(local_path,item.filename))
                else:
                    for item in item_list:
                        mode = item.st_mode
                        if S_ISDIR(mode):
                            if not os.path.isdir(item.filename):
                                os.makedirs(item.filename, exist_ok=True)
                            self.download_from_path(os.path.join(remote_path,item.filename))
                        else:
                            self.sftp.get(os.path.join(remote_path,item.filename),item.filename)            
            if S_ISREG(fileattr.st_mode):
                print('is File' )
                if local_path != None:
                    self.sftp.get(remote_path,os.path.join(local_path,remote_path.split('/')[-1]))
                else:
                    self.sftp.get(remote_path,remote_path.split('/')[-1])

        def connect(self, host, username, key, duo_option):
            try:
                p_key = 0
                try:
                    p_key = paramiko.Ed25519Key.from_private_key_file(key)
                except Exception as e:
                    print('Cannot read SSH key as path') 
                    try:
                        p_key = paramiko.Ed25519Key.from_private_key(io.StringIO(key))
                    except Exception as e:
                        print('Cannot read SSH key as string with error: ' + str(e))
                        exit(0)
                    
            except Exception as e:
                print('Cannot read SSH key with error: ' + str(e))
                exit(0)
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sys.stdin = StringIO(str(duo_option))
                self.ssh.connect(hostname=host, username=username, pkey=p_key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
                print('Logged in to server') 
                self.sftp = self.ssh.open_sftp()        
                return self.ssh, self.sftp  
            except paramiko.SSHException as e:
                print('Cannot login with error ' + str(e))
                print('Please check key or OTP on mobile')
                exit(0)
       
    import minio
    from minio import Minio
    import re
    import time
    class StorageClient():
        minio_client = 0 
       
        def connect(self,host='host:port',
                  username='key',
                  password='secret'):
            self.minio_client = Minio(endpoint=host,
                    access_key=username,
                    secret_key=password,
                    secure=False)
          
        def make_bucket(self,bucket_name):
            try:
              found = self.minio_client.bucket_exists(bucket_name)
              if not found:
                  self.minio_client.make_bucket(bucket_name)
              else:
                  print('Bucket ' + bucket_name + ' already exists')
            except minio.error.BucketAlreadyExists:
              pass
            except minio.error.BucketAlreadyOwnedByYou:
              pass
              
        def is_file_existed(self,bucket_name,file_path):
            try:
                stat = self.minio_client.stat_object(storage_bucket, file_path)
                print(os.path.join(bucket_name,stat.object_name) + ' exists')
                return True
            except Exception as err:
                print(os.path.join(bucket_name,file_path) + ' does not exist')
                return False
                
        def upload_from_path(self,bucket_name,local_path,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(local_path,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(local_path,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(local_path,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(local_path,file_path)))
                    else:
                        if sub_folder == None:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path))
                        else:
                            self.upload_from_path(bucket_name,os.path.join(local_path,file_path),sub_folder)
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,local_path,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + local_path)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,local_path),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,local_path))
          
        def upload_from_path_and_rename(self,bucket_name,local_path,new_name,sub_folder=None):
            if os.path.isdir(local_path):
                for file_path in os.listdir(local_path):
                    if os.path.isfile(file_path):
                        if sub_folder == None:
                            self.minio_client.fput_object(bucket_name,os.path.join(new_name,file_path), file_path)
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(new_name,file_path))
                        else:
                            self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,os.path.join(new_name,file_path)),os.path.join(local_path,file_path))
                            print('Uploaded from ' + file_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(new_name,file_path)))                    
                    else:
                        if sub_folder == None:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path))
                        else:
                            self.upload_from_path_and_rename(bucket_name,os.path.join(local_path,file_path),os.path.join(new_name,file_path),sub_folder)
                        
            else:
                if sub_folder == None:
                    self.minio_client.fput_object(bucket_name,new_name,local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + new_name)
                else:
                    self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,new_name),local_path)
                    print('Uploaded from ' + local_path + ' to ' + bucket_name + '/' + os.path.join(sub_folder,new_name))
                    
        def download_from_path(self,bucket_name,remote_path,local_path=None):
            dest_path = ''
            if local_path == None:
                dest_path = os.getcwd()
            else:
                dest_path = local_path
                
            print(os.path.join(dest_path,remote_path))
            if not os.path.isdir(os.path.join(dest_path,remote_path)):
                os.makedirs(os.path.join(dest_path,remote_path), exist_ok=True)
                print('made dir ' + remote_path)
            objects = storage_client.minio_client.list_objects(bucket_name, prefix=remote_path,recursive=True)
            for obj in objects:
                self.download_file_path(bucket_name, obj.object_name, os.path.join(dest_path,obj.object_name))  
                print('Downloaded from ' + os.path.join(bucket_name,obj.object_name) + ' to ' + os.path.join(dest_path,obj.object_name))
        
        def upload_file_path(self,bucket_name,file_path,local_path,sub_folder=None):
            if sub_folder == None:
                self.minio_client.fput_object(bucket_name,file_path,local_path)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from ' + local_path)
            else:
                self.minio_client.fput_object(bucket_name,os.path.join(sub_folder,file_path),local_path)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from ' + local_path)
          
        def download_file_path(self,bucket_name,file_path,local_path):
            self.minio_client.fget_object(bucket_name,file_path,local_path)
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to ' + local_path)        
            
        def upload_file(self,bucket_name,file_path,data,length,sub_folder=None):
            if sub_folder == None:
                self.minio_client.put_object(bucket_name, file_path, data, length)
                print('Uploaded to ' + bucket_name + '/' + file_path + ' from buffer')
            else:
                self.minio_client.put_object(bucket_name, os.path.join(sub_folder,file_path), data, length)
                print('Uploaded to ' + bucket_name + '/' + os.path.join(sub_folder,file_path) + ' from buffer')
            
          
        def download_file(self,bucket_name,file_path):
            print('Downloaded from ' + bucket_name + '/' + file_path + ' to buffer')
            return self.minio_client.get_object(bucket_name, file_path)
            
        def upload_folder_from_sftp(self,pipeline_client,sftp_folder_parent_path,sftp_folder_name,bucket_name,file_path,sub_folder=None):
            item_list = pipeline_client.sftp.listdir_attr(os.path.join(sftp_folder_parent_path,sftp_folder_name))
            for item in item_list:
                mode = item.st_mode
                if S_ISDIR(mode):
                    print('dir ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    self.upload_folder_from_sftp(pipeline_client,os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename,bucket_name,os.path.join(file_path,item.filename))
                else:
                    print('file ',os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename),os.path.join(file_path,item.filename))
                    with pipeline_client.sftp.open(os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename), "rb") as fl:
                        fl.prefetch()
                        if sub_folder == None:
                            self.upload_file(bucket_name, os.path.join(file_path,item.filename), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(file_path,item.filename))
                        else:
                            self.upload_file(bucket_name, os.path.join(sub_folder,os.path.join(file_path,item.filename)), fl, fl.stat().st_size)
                            print('Uploaded from remote ' + os.path.join(os.path.join(sftp_folder_parent_path,sftp_folder_name),item.filename) + ' to ' + bucket_name + '/' + os.path.join(sub_folder,os.path.join(file_path,item.filename)))
                    
        def transfer_folder_to_sftp(self,pipeline_client,bucket_name,folder,remote_parent_path):
            objects = self.minio_client.list_objects(bucket_name, prefix=folder)
            for obj in objects:
                if obj.is_dir:
                    print('dir ',os.path.join(bucket_name,obj.object_name),os.path.join(remote_parent_path,obj.object_name))
                    if not pipeline_client.is_dir_path_existed_remotely(os.path.join(remote_parent_path,obj.object_name)):
                        pipeline_client.mkdir_nested_remotely(os.path.join(remote_parent_path,obj.object_name))                
                    print(os.path.join(bucket_name,obj.object_name) + ' is dir')
                    self.transfer_folder_to_sftp(pipeline_client,bucket_name,obj.object_name,remote_parent_path)
                else:
                    print('file ',bucket_name + '/' + obj.object_name,os.path.join(remote_parent_path,obj.object_name))
                    file = self.download_file(bucket_name, obj.object_name)
                    pipeline_client.sftp.putfo(file, os.path.join(remote_parent_path,obj.object_name))
                    print('Transferred from ' + bucket_name + '/' + obj.object_name + ' to ' + os.path.join(remote_parent_path,obj.object_name))
                    
        def upload_file_from_sftp(self,pipeline_client,sftp_file_path,bucket_name,sub_folder=None):
            with pipeline_client.sftp.open(sftp_file_path, "rb") as fl:
                fl.prefetch()
                if sub_folder == None:
                    self.upload_file(bucket_name, sftp_file_path.split('/')[-1], fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + bucket_name + '/' + sftp_file_path.split('/')[-1])  
                else:
                    self.upload_file(bucket_name, os.path.join(sub_folder,sftp_file_path.split('/')[-1]), fl, fl.stat().st_size)
                    print('Uploaded from remote ' + sftp_file_path + ' to ' + os.path.join(bucket_name,os.path.join(sub_folder,sftp_file_path.split('/')[-1])))          
                    
        def transfer_file_to_sftp(self,pipeline_client,bucket_name,file_path,remote_path):
            file = self.download_file(bucket_name, file_path)
            pipeline_client.sftp.putfo(file, remote_path)
            print('Transferred from ' + bucket_name + '/' + remote_path + ' to ' + remote_path)
               
    #Login to remote
    pipeline_client = PipelineClient()
    ssh, sftp = pipeline_client.connect(remote_auth['ssh_address'], remote_auth['ssh_username'], remote_auth['ssh_key'], str(remote_auth['ssh_duo_option']))
    pipeline_client.run_cmd_remotely('ls -l')
    
    #Working with folders on remote
    for project_index,project in enumerate(remote_storages):
        for project_name in project.keys():
            remote_work_name = project_name
            storage_client = StorageClient()
            storage_client.connect(remote_auth['minio_address'],remote_auth['minio_key'],remote_auth['minio_secret'])
            storage_bucket = remote_work_name.lower()
            storage_bucket = re.sub('[^0-9a-zA-Z]+', '', storage_bucket)
            storage_client.make_bucket(storage_bucket)
            for sim_index,simulation in enumerate(project[project_name]):
                for sim_name in simulation.keys():
                    remote_sim = remote_sims[project_index][project_name][sim_index][sim_name]
                    print('Checking remote folders')
                    for dirs in simulation[sim_name]:
                        for work_dir in dirs.keys():
                            for remote_path in dirs[work_dir]:
                                item_tar_path = work_dir + '.tar.gz'           
                                storage_path = dirs[work_dir][remote_path]
                                if remote_sim['using_storage'] == 'True':
                                    if remote_sim['using_tar'] == 'True':
                                        print('Sync tar files to remote and storage')                             
                                        if not pipeline_client.is_file_path_existed_remotely(remote_path):
                                            pipeline_client.compress_file_path_remotely(remote_sim['work_path'], work_dir)
                                        else:
                                            print(remote_path + ' exists')
                                        if not storage_client.is_file_existed(storage_bucket, storage_path.split(storage_bucket)[-1]):
                                            storage_client.upload_file_from_sftp(pipeline_client, os.path.join(remote_sim['work_path'], item_tar_path),storage_bucket,sim_name)     
                                        else:
                                            print(storage_path + ' exists')
                                    else:
                                        print('Sync folders to remote and storage')
                                        storage_client.upload_folder_from_sftp(pipeline_client, remote_sim['work_path'],work_dir,storage_bucket,work_dir,sim_name)
                                else:
                                    if remote_sim['using_tar'] == 'True':
                                        print('Sync tar files to remote')
                                        if not pipeline_client.is_file_path_existed_remotely(remote_path):
                                            pipeline_client.compress_file_path_remotely(remote_sim['work_path'], work_dir)
                                        else:
                                            print(remote_path + ' exists')
                                    else:
                                        print('Not using tar or storage')   
                                        
                                #Download to local path
                                print('Final check')
                                if not pipeline_client.is_file_path_existed_remotely(os.path.join(remote_sim['work_path'], item_tar_path)):
                                    pipeline_client.compress_file_path_remotely(remote_sim['work_path'], work_dir)
                                else:
                                    print(os.path.join(remote_sim['work_path'], item_tar_path) + ' exists')
                                if not storage_client.is_file_existed(storage_bucket, storage_path.split(storage_bucket)[-1]):
                                    storage_client.upload_file_from_sftp(pipeline_client, os.path.join(remote_sim['work_path'], item_tar_path),storage_bucket,sim_name)     
                                else:
                                    print(storage_path + ' exists')
                                # print('Download all files to local path ' + remote_sim['local_path'])
                                # storage_client.download_from_path(storage_bucket,sim_name,remote_sim['local_path'])
    
    remote_output = namedtuple('outputs', ['remote_auth',
                                           'remote_repo',
                                           'remote_sims',
                                           'remote_binaries',
                                           'remote_dirs',
                                           'remote_files',
                                           'remote_storages',
                                           'remote_tasks',
                                           'remote_plots'])        
    return remote_output(remote_auth,remote_repo,remote_sims,remote_binaries,remote_dirs,remote_files,remote_storages,remote_tasks,remote_plots)
                   
def pipeline(pipeline_config_url):
    pipeline_config_download_task = download_op(url = pipeline_config_url)
    pipeline_config_download_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    step_1_parse_config_op = comp.create_component_from_func(
            func = step_1_parse_config,
            base_image='python:3.8',
            packages_to_install=['pyaml','requests'])    
    step_1_parse_config_task = step_1_parse_config_op(pipeline_config = pipeline_config_download_task.outputs['data'])
    step_1_parse_config_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    step_2_make_dirs_op = comp.create_component_from_func(
            func = step_2_make_dirs,
            base_image='python:3.8',
            packages_to_install=['paramiko'])    
    step_2_make_dirs_task = step_2_make_dirs_op(remote_auth = step_1_parse_config_task.outputs['remote_auth'],
                                                remote_repo = step_1_parse_config_task.outputs['remote_repo'],
                                                remote_sims = step_1_parse_config_task.outputs['remote_sims'],
                                                remote_binaries = step_1_parse_config_task.outputs['remote_binaries'],
                                                remote_dirs = step_1_parse_config_task.outputs['remote_dirs'],
                                                remote_files = step_1_parse_config_task.outputs['remote_files'],
                                                remote_storages = step_1_parse_config_task.outputs['remote_storages'],
                                                remote_tasks = step_1_parse_config_task.outputs['remote_tasks'],
                                                remote_plots = step_1_parse_config_task.outputs['remote_plots']
                                                )
    step_2_make_dirs_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    step_3_build_binary_op = comp.create_component_from_func(
            func = step_3_build_binary,
            base_image='python:3.8',
            packages_to_install=['paramiko','minio'])    
    step_3_build_binary_task = step_3_build_binary_op(remote_auth = step_2_make_dirs_task.outputs['remote_auth'],
                                                    remote_repo = step_2_make_dirs_task.outputs['remote_repo'],
                                                    remote_sims = step_2_make_dirs_task.outputs['remote_sims'],
                                                    remote_binaries = step_2_make_dirs_task.outputs['remote_binaries'],
                                                    remote_dirs = step_2_make_dirs_task.outputs['remote_dirs'],
                                                    remote_files = step_2_make_dirs_task.outputs['remote_files'],
                                                    remote_storages = step_2_make_dirs_task.outputs['remote_storages'],
                                                    remote_tasks = step_2_make_dirs_task.outputs['remote_tasks'],
                                                    remote_plots = step_2_make_dirs_task.outputs['remote_plots']
                                                    )
    step_3_build_binary_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    step_4_run_tasks_op = comp.create_component_from_func(
            func = step_4_run_tasks,
            base_image='python:3.8',
            packages_to_install=['paramiko','minio','numpy','pandas','pyaml','matplotlib'])
    # step_4_run_tasks_task = step_4_run_tasks_op(remote_auth = step_1_parse_config_task.outputs['remote_auth'],
    #                                             remote_repo = step_1_parse_config_task.outputs['remote_repo'],
    #                                             remote_sims = step_1_parse_config_task.outputs['remote_sims'],
    #                                             remote_binaries = step_1_parse_config_task.outputs['remote_binaries'],
    #                                             remote_dirs = step_1_parse_config_task.outputs['remote_dirs'],
    #                                             remote_files = step_1_parse_config_task.outputs['remote_files'],
    #                                             remote_storages = step_1_parse_config_task.outputs['remote_storages'],
    #                                             remote_tasks = step_1_parse_config_task.outputs['remote_tasks'],
    #                                             remote_plots = step_1_parse_config_task.outputs['remote_plots']
    #                                             )
    # step_4_run_tasks_task = step_4_run_tasks_op(remote_auth = step_2_make_dirs_task.outputs['remote_auth'],
    #                                                 remote_repo = step_2_make_dirs_task.outputs['remote_repo'],
    #                                                 remote_sims = step_2_make_dirs_task.outputs['remote_sims'],
    #                                                 remote_binaries = step_2_make_dirs_task.outputs['remote_binaries'],
    #                                                 remote_dirs = step_2_make_dirs_task.outputs['remote_dirs'],
    #                                                 remote_files = step_2_make_dirs_task.outputs['remote_files'],
    #                                                 remote_storages = step_2_make_dirs_task.outputs['remote_storages'],
    #                                                 remote_tasks = step_2_make_dirs_task.outputs['remote_tasks'],
    #                                                 remote_plots = step_2_make_dirs_task.outputs['remote_plots']
    #                                                 )
    step_4_run_tasks_task = step_4_run_tasks_op(remote_auth = step_3_build_binary_task.outputs['remote_auth'],
                                                    remote_repo = step_3_build_binary_task.outputs['remote_repo'],
                                                    remote_sims = step_3_build_binary_task.outputs['remote_sims'],
                                                    remote_binaries = step_3_build_binary_task.outputs['remote_binaries'],
                                                    remote_dirs = step_3_build_binary_task.outputs['remote_dirs'],
                                                    remote_files = step_3_build_binary_task.outputs['remote_files'],
                                                    remote_storages = step_3_build_binary_task.outputs['remote_storages'],
                                                    remote_tasks = step_3_build_binary_task.outputs['remote_tasks'],
                                                    remote_plots = step_3_build_binary_task.outputs['remote_plots']
                                                    )
    step_4_run_tasks_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    step_5_save_outputs_op = comp.create_component_from_func(
            func = step_5_save_outputs,
            base_image='python:3.8',
            packages_to_install=['paramiko','minio','pyaml'])
    step_5_save_outputs_task = step_5_save_outputs_op(remote_auth = step_4_run_tasks_task.outputs['remote_auth'],
                                                    remote_repo = step_4_run_tasks_task.outputs['remote_repo'],
                                                    remote_sims = step_4_run_tasks_task.outputs['remote_sims'],
                                                    remote_binaries = step_4_run_tasks_task.outputs['remote_binaries'],
                                                    remote_dirs = step_4_run_tasks_task.outputs['remote_dirs'],
                                                    remote_files = step_4_run_tasks_task.outputs['remote_files'],
                                                    remote_storages = step_4_run_tasks_task.outputs['remote_storages'],
                                                    remote_tasks = step_4_run_tasks_task.outputs['remote_tasks'],
                                                    remote_plots = step_4_run_tasks_task.outputs['remote_plots']
                                                    )
    step_5_save_outputs_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    # step_6_run_plots_op = comp.create_component_from_func(
    #         func = step_6_run_plots,
    #         base_image='python:3.8',
    #         packages_to_install=['paramiko','minio','numpy','pandas','pyaml','matplotlib','seaborn'])
    # step_6_run_plots_task = step_6_run_plots_op(remote_auth = step_1_parse_config_task.outputs['remote_auth'],
    #                                             remote_repo = step_1_parse_config_task.outputs['remote_repo'],
    #                                             remote_sims = step_1_parse_config_task.outputs['remote_sims'],
    #                                             remote_binaries = step_1_parse_config_task.outputs['remote_binaries'],
    #                                             remote_dirs = step_1_parse_config_task.outputs['remote_dirs'],
    #                                             remote_files = step_1_parse_config_task.outputs['remote_files'],
    #                                             remote_storages = step_1_parse_config_task.outputs['remote_storages'],
    #                                             remote_tasks = step_1_parse_config_task.outputs['remote_tasks'],
    #                                             remote_plots = step_1_parse_config_task.outputs['remote_plots']
    #                                             )
    # step_6_run_plots_task = step_6_run_plots_op(remote_auth = step_5_save_outputs_task.outputs['remote_auth'],
    #                                                 remote_repo = step_5_save_outputs_task.outputs['remote_repo'],
    #                                                 remote_sims = step_5_save_outputs_task.outputs['remote_sims'],
    #                                                 remote_binaries = step_5_save_outputs_task.outputs['remote_binaries'],
    #                                                 remote_dirs = step_5_save_outputs_task.outputs['remote_dirs'],
    #                                                 remote_files = step_5_save_outputs_task.outputs['remote_files'],
    #                                                 remote_storages = step_5_save_outputs_task.outputs['remote_storages'],
    #                                                 remote_tasks = step_5_save_outputs_task.outputs['remote_tasks'],
    #                                                 remote_plots = step_5_save_outputs_task.outputs['remote_plots']
    #                                                 )
    # step_6_run_plots_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    # step_7_download_data_op = comp.create_component_from_func(
    #         func = step_7_download_data,
    #         base_image='python:3.8',
    #         packages_to_install=['paramiko','minio','numpy','pandas','pyaml','matplotlib','seaborn'])
    # step_7_download_data_task = step_7_download_data_op(remote_auth = step_6_run_plots_task.outputs['remote_auth'],
    #                                                 remote_repo = step_6_run_plots_task.outputs['remote_repo'],
    #                                                 remote_sims = step_6_run_plots_task.outputs['remote_sims'],
    #                                                 remote_binaries = step_6_run_plots_task.outputs['remote_binaries'],
    #                                                 remote_dirs = step_6_run_plots_task.outputs['remote_dirs'],
    #                                                 remote_files = step_6_run_plots_task.outputs['remote_files'],
    #                                                 remote_storages = step_6_run_plots_task.outputs['remote_storages'],
    #                                                 remote_tasks = step_6_run_plots_task.outputs['remote_tasks'],
    #                                                 remote_plots = step_6_run_plots_task.outputs['remote_plots']
    #                                                 )
    # step_7_download_data_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
#%%
import paramiko
import os
import subprocess
    
#Pipeline config
pipeline_configs = {
    'pipeline_config_url' : 'https://www.dropbox.com/s/t95loij4cuy9f7r/pipeline_v5.yml'
    }

#Run pipeline
client.create_run_from_pipeline_func(pipeline, arguments=pipeline_configs)

#%%
if __name__ == '__main__':
    # Compiling the pipeline
    kfp.compiler.Compiler().compile(pipeline, __file__ + '.yaml')    