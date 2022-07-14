import kfp.components as comp
import kfp
from typing import NamedTuple

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

download_op = kfp.components.load_component_from_url(
'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/contrib/web/Download/component.yaml')

pipeline_config_url = \
'https://raw.githubusercontent.com/KienTTran/PSU-CIDD-Malaria-Simulation-Scripts/master/python/Pipeline/Kubeflow/Masim/pipeline.yml'

ssh_key_url = \
''

def parse_pipeline_config_func(pipeline_config: comp.InputArtifact()) -> NamedTuple('outputs', [
                                                                                ('remote_repo', list),
                                                                                ('remote_exe_build', list),
                                                                                ('remote_exe_run', list),
                                                                                ('remote_files', list),
                                                                                ('remote_dirs', list),
                                                                                ('remote_generators', list)]):
    import yaml
    import os
    from collections import namedtuple
    
    print('parsing pipeline')
    
    params = 0
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
            
    cluster_username = params['ssh']['username']
    cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
    
    #Repo
    cluster_repo = []
    cluster_exe_build = []
    cluster_exe_run = []
    for pair in params['project']:
        if type(pair) == str:
            print('Project is empty')
        else:
            for p_key in pair.keys():
                if pair[p_key] == None:
                    print('Project is empty')
                else:
                    pj_path = p_key
                    pj_exe = pair[p_key]['exe']
                    if pj_exe == None:
                        print('Execution is empty')
                    else:
                        pj_exe_build_path = pair[p_key]['exe']['build']['path']
                        pj_exe_run_path = pair[p_key]['exe']['run']['path']
                        if pj_exe_build_path == None or pj_exe_run_path == None:
                            print('Execution build/run path is empty')
                        else:
                            #Build
                            parameter_str = ''
                            try:
                                pj_exe_build_parameters = pair[p_key]['exe']['build']['parameters']
                                if pj_exe_build_parameters != None:
                                    for parameter in pj_exe_build_parameters:
                                        parameter_str += ' ' + parameter
                            except Exception as e:
                                print('Missing ' + str(e) + ', use empty parameters')
                            pj_exe_build_with_parameters = pj_exe_build_path + ' ' + parameter_str
                            cluster_exe_build.append({os.path.join(cluster_home_path,pj_path):pj_exe_build_with_parameters})
                            #Run
                            parameter_str = ''
                            try:
                                pj_exe_run_parameters = pair[p_key]['exe']['run']['parameters']
                                if pj_exe_run_parameters != None:
                                    for parameter in pj_exe_run_parameters:
                                        parameter_str += ' ' + parameter
                            except Exception as e:
                                print('Missing ' + str(e) + ', use empty parameters')
                            pj_exe_run_with_parameters = pj_exe_run_path + ' ' + parameter_str
                            cluster_exe_run.append({os.path.join(cluster_home_path,pj_path):pj_exe_run_with_parameters})
                                
                        pj_repo = pair[p_key]['repo']
                        if pj_repo == None:
                            print('Repo is empty')
                        else:
                            pj_repo_url = pair[p_key]['repo']['url']
                            if pj_repo_url == None:
                                print('Repo URL is empty')
                            else:
                                pj_repo_branch = pair[p_key]['repo']['branch']
                                pj_repo_git = ''
                                if pj_repo_branch == None:
                                    pj_repo_git = pj_repo_url
                                else:
                                    pj_repo_git = pj_repo_url + ' -b ' + pj_repo_branch
                                cluster_repo.append({os.path.join(cluster_home_path,pj_path):pj_repo_git})
                    
    
    #Files
    cluster_files = []
    cluster_dirs = []
    for pair in params['remote']:
        if type(pair) == str:
            cluster_dirs.append(os.path.join(cluster_home_path,pair))
        else:
            for key in pair.keys():
                path = key
                src_files = pair[key]
                cluster_dirs.append(os.path.join(cluster_home_path,path))
                for src_file in src_files:
                    cluster_files.append({os.path.join(cluster_home_path,path) : src_file})
                    print(src_file + ' --> ' + os.path.join(cluster_home_path,path))
                    
    #Generators                    
    cluster_generators = []
    for gen_pair in params['generator']:
        for gen_key in gen_pair.keys():
            working_path = gen_key
            gen_value = gen_pair[gen_key]
            script_with_parameters = ''
            is_valid = False
            if gen_value != None:
                for value in gen_value:
                    for v_key in value.keys():
                        script = ''
                        script_name = ''
                        if v_key =='bash':
                            bash_str = ''
                            if value[v_key] != None:
                                script_name = value[v_key]
                                script = script_name
                                is_valid = True
                        elif v_key == 'script':
                            if value[v_key] != None:
                                try:
                                    script_name = value[v_key]['name']
                                    script_exe = ''
                                    parameter_str = ''
                                    if script_name != None and script_name != '':
                                        script_ext = script_name.split('.')[-1]
                                        if script_ext == 'py':
                                            script_exe = 'python3'
                                        if script_ext == 'sh':
                                            script_exe = 'sh'
                                        try:
                                            script_parameters = value[v_key]['parameters']
                                            if script_parameters != None:
                                                for parameter in script_parameters:
                                                    parameter_str += ' ' + parameter
                                            else:
                                                print('No parameters')     
                                        except Exception as e:
                                            print('Missing: ' + str(e) + ', use empty parameters')
                                        script = script_exe + ' ' + script_name + parameter_str
                                        is_valid = True
                                    else:
                                        print('Script name is empty, skipped')   
                                except Exception as e:
                                    print('Missing: ' + str(e) + ', skipped')
                            else:
                                print('Script is empty, skipped')
                        if script_with_parameters == '':
                            script_with_parameters = script
                        else:
                            script_with_parameters = script_with_parameters + ' && ' + script
                if is_valid:
                    cluster_generators.append({os.path.join(cluster_home_path,working_path):script_with_parameters})
            else:
                print('Missing script when path is available, skipped')
                 
    remote_output = namedtuple('outputs', ['remote_repo','remote_exe_build','remote_exe_run','remote_files','remote_dirs','remote_generators']) 
    
    #Repo
    for file_path in cluster_repo:
        for key in file_path.keys():
            print('Cluster repo (clone): ' + key + ' --> ' + file_path[key]) 
    
    #Build       
    for file_path in cluster_exe_build:
        for key in file_path.keys():
            print('Cluster exe (build): ' + key + ' --> ' + file_path[key]) 
            
    #Run       
    for file_path in cluster_exe_run:
        for key in file_path.keys():
            print('Cluster exe (run): ' + key + ' --> ' + file_path[key])          
    
    #Files
    for file_path in cluster_files:
        for key in file_path.keys():
            print('Cluster file path (transfer): ' + key + ' --> ' + file_path[key])
            
    #Dirs
    for file_path in cluster_dirs:
        print('Cluster file path (create): ' + file_path)
        
    #Generators
    for generators in cluster_generators:
        for working_path in generators.keys():
            print('cd ' + working_path + ' ' + generators[working_path])
                
    return remote_output(cluster_repo,cluster_exe_build,cluster_exe_run,cluster_files,cluster_dirs,cluster_generators)
    

def run_on_cluster_func(pipeline_config: comp.InputArtifact(),
                        ssh_key: comp.InputArtifact(),
                        remote_repo: list,
                        remote_exe_build: list,
                        remote_exe_run: list,
                        remote_files: list,
                        remote_dirs: list,
                        remote_generators: list):
    import paramiko
    import yaml
    import os
    
    print('Running on cluster')
    
    def cmd_git_clone(repo_info, dir_dst):
        return 'git clone' + repo_info + ' ' + dir_dst
    
    def cmd_wget(file_src, dir_dst):
        return 'wget ' + file_src + ' -P ' + dir_dst
    
    def cmd_generator(working_dir, generator_script):
        if '.' in generator_script.split(' ')[0]:
            gen_ext = generator_script.split(' ')[0].split['.'][1]
            if gen_ext == 'py':
                return 'cd ' + working_dir + '; python3 ' + generator_script
        else:#is bash file
            return 'cd ' + working_dir + '; ' + generator_script
    
    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0
        
        def disconnect(self):
            self.ssh.close()
            self.sftp.close()
        
        def run_cmd_remotely(self,command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command,get_pty=True)
            for line in stdout.readlines():
                print(line)
            err = stderr.read().decode()
            if err:
                print(err)
                
        def is_dir_path_existed_remotely(self,file_path):
            try:
                self.sftp.chdir(file_path) # sub-directory exists
                print(file_path + ' exists')
                return True
            except IOError:
                print(file_path + ' does not exist')
                return False
            
        def is_file_path_existed_remotely(self,file_path):
            try:
                self.sftp.stat(file_path) # sub-directory exists
                print(file_path + ' exists')
                return True
            except IOError:
                print(file_path + ' does not exist')
                return False
                
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
                self.sftp.chdir(remote_directory) # sub-directory exists
            except IOError:
                dirname, basename = os.path.split(remote_directory.rstrip('/'))
                self.mkdir_nested(dirname) # make parent directories
                self.sftp.mkdir(basename) # sub-directory missing, so created it
                self.sftp.chdir(basename)
                return True
                
        def connect(self, host, username, key):
            if key != '':
                try:
                    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    key = paramiko.Ed25519Key.from_private_key_file(key)
                    self.ssh.connect(hostname=host, username=username, pkey=key)
                    print('Logged in to server')
                except (paramiko.SSHException) as e:
                    print('Cannot login with error ' + str(e))  
                    print('Please check key or OTP on mobile')
                    exit(0)     
            else:
                print('Please provide SSH key path')
                exit(0)
                
            self.sftp = self.ssh.open_sftp()
            return self.ssh, self.sftp
    
    params = 0    
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
    
    #ssh info
    cluster_address = params['ssh']['address']
    cluster_username = params['ssh']['username']
    cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
    print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)
        
    
    for repo in remote_repo:
        for working_path in repo.keys():
            print('git clone ' + repo[working_path] + ' ' + working_path)
            
    for build in remote_exe_build:
        for working_path in build.keys():
            print('build ' + working_path + ' ./' + build[working_path])
    
    for run in remote_exe_run:
        for working_path in run.keys():
            print('run ' + working_path + ' ./' + run[working_path])
            
    for dirs in remote_dirs:
        print('mkdir_nest ' + dirs)
        
    for files in remote_files:
        for working_path in files.keys():
            print('wget ' + files[working_path] + ' -P ' + working_path)
    
    for generators in remote_generators:
        for working_path in generators.keys():
            print('cd ' + working_path + ' ' + generators[working_path])
            
    # #Connect to server
    # client = PipelineClient()
    # ssh, sftp = client.connect(params['ssh']['address'], params['ssh']['username'],ssh_key)
    # client.run_cmd_remotely('ls -l')    
    
    # #Pull repo
    # for repos in remote_repos:
    #     for working_path in repos.keys():
    #         client.run_cmd_remotely(cmd_git_clone(repos[working_path],working_path))
    
    # #Create dirs
    # for file_path in remote_dirs:
    #     client.mkdir_nested(file_path)
    #     print('Created cluster path: ' + file_path)
        
    # #Copy files
    # for files in remote_files:
    #     for working_path in files.keys():
    #         client.run_cmd_remotely(cmd_wget(files[working_path], working_path))
            
    # #Run generators    
    # for generators in remote_generators:
    #     for working_path in generators.keys():
    #         client.run_cmd_remotely(cmd_generator(working_path,generators[working_path]))
    
    
def pipeline():        
    pipeline_config_download_task = download_op(url = pipeline_config_url)
    pipeline_config_download_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    ssh_key_download_task = download_op(url = ssh_key_url)
    ssh_key_download_task.execution_options.caching_strategy.max_cache_staleness = "P0D"
    
    parse_pipeline_config_op = comp.create_component_from_func(
            func = parse_pipeline_config_func,
            output_component_file='components/parse_remote_file_comp.yaml',
            base_image='python:3.8',
            packages_to_install=['pyaml'])
    
    parse_pipeline_config_task = parse_pipeline_config_op(pipeline_config = pipeline_config_download_task.outputs['data'])
    
    run_on_cluster_op = comp.create_component_from_func(
            func = run_on_cluster_func,
            output_component_file='components/run_on_cluster_comp.yaml', # This is optional. It saves the component spec for future use.
            base_image='python:3.8',
            packages_to_install=['paramiko','pyaml'])
    
    run_on_cluster_task = run_on_cluster_op(pipeline_config = pipeline_config_download_task.outputs['data'],
                                            ssh_key = ssh_key_download_task.outputs['data'],
                                            remote_repo = parse_pipeline_config_task.outputs['remote_repo'],
                                            remote_exe_build = parse_pipeline_config_task.outputs['remote_exe_build'],
                                            remote_exe_run = parse_pipeline_config_task.outputs['remote_exe_run'],
                                            remote_files = parse_pipeline_config_task.outputs['remote_files'],
                                            remote_dirs = parse_pipeline_config_task.outputs['remote_dirs'],
                                            remote_generators = parse_pipeline_config_task.outputs['remote_generators'],
                                            )
    

#%%
client.create_run_from_pipeline_func(pipeline, arguments={})

    #%%
if __name__ == '__main__':
    # Compiling the pipeline
    kfp.compiler.Compiler().compile(pipeline, __file__ + '.yaml')
    
#%%
import yaml
import os
from collections import namedtuple

params = 0
print("Reading " + 'pipeline.yml')
with open('pipeline.yml','r') as file:
    params =  yaml.full_load(file)

cluster_username = params['ssh']['username']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username

cluster_repo = []
cluster_exe_build = []
cluster_exe_run = []
for pair in params['project']:
    if type(pair) == str:
        print('Project is empty')
    else:
        for p_key in pair.keys():
            if pair[p_key] == None:
                print('Project is empty')
            else:
                pj_path = p_key
                pj_exe = pair[p_key]['exe']
                if pj_exe == None:
                    print('Execution is empty')
                else:
                    pj_exe_build_path = pair[p_key]['exe']['build']['path']
                    pj_exe_run_path = pair[p_key]['exe']['run']['path']
                    if pj_exe_build_path == None or pj_exe_run_path == None:
                        print('Execution build/run path is empty')
                    else:
                        #Build
                        parameter_str = ''
                        try:
                            pj_exe_build_parameters = pair[p_key]['exe']['build']['parameters']
                            if pj_exe_build_parameters != None:
                                for parameter in pj_exe_build_parameters:
                                    parameter_str += ' ' + parameter
                        except Exception as e:
                            print('Missing ' + str(e) + ', use empty parameters')
                        pj_exe_build_with_parameters = pj_exe_build_path + ' ' + parameter_str
                        cluster_exe_build.append({os.path.join(cluster_home_path,pj_path):pj_exe_build_with_parameters})
                        #Run
                        parameter_str = ''
                        try:
                            pj_exe_run_parameters = pair[p_key]['exe']['run']['parameters']
                            if pj_exe_run_parameters != None:
                                for parameter in pj_exe_run_parameters:
                                    parameter_str += ' ' + parameter
                        except Exception as e:
                            print('Missing ' + str(e) + ', use empty parameters')
                        pj_exe_run_with_parameters = pj_exe_run_path + ' ' + parameter_str
                        cluster_exe_run.append({os.path.join(cluster_home_path,pj_path):pj_exe_run_with_parameters})
                            
                    pj_repo = pair[p_key]['repo']
                    if pj_repo == None:
                        print('Repo is empty')
                    else:
                        pj_repo_url = pair[p_key]['repo']['url']
                        if pj_repo_url == None:
                            print('Repo URL is empty')
                        else:
                            pj_repo_branch = pair[p_key]['repo']['branch']
                            pj_repo_git = ''
                            if pj_repo_branch == None:
                                pj_repo_git = pj_repo_url
                            else:
                                pj_repo_git = pj_repo_url + ' -b ' + pj_repo_branch
                            cluster_repo.append({os.path.join(cluster_home_path,pj_path):pj_repo_git})
                
    
#%%
import yaml
import os
from collections import namedtuple

params = 0
print("Reading " + 'pipeline.yml')
with open('pipeline.yml','r') as file:
    params =  yaml.full_load(file)
        
cluster_username = params['ssh']['username']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username

cluster_files = []
cluster_mkdir = []
for pair in params['remote']:
    if type(pair) == str:
        cluster_mkdir.append(os.path.join(cluster_home_path,pair))
    else:
        for key in pair.keys():
            path = key
            src_files = pair[key]
            cluster_mkdir.append(os.path.join(cluster_home_path,path))
            for src_file in src_files:
                cluster_files.append({os.path.join(cluster_home_path,path) : src_file})
                print(src_file + ' --> ' + os.path.join(cluster_home_path,path))
             
remote_path_output = namedtuple('outputs', ['remote_files']) 
for file_path in cluster_files:
    for key in file_path.keys():
        print('Cluster file path (transfer): ' + key + ' --> ' + file_path[key])   
for file_path in cluster_mkdir:
    print('Cluster file path (create): ' + file_path)
    
#%%
import yaml
import os

def cmd_generator(working_dir, generator_script):
    return 'cd ' + working_dir + '; ' + generator_script
        
params = 0    
print("Reading " + 'pipeline.yml')
with open('pipeline.yml','r') as file:
    params =  yaml.full_load(file)
    
cluster_username = params['ssh']['username']
cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
cluster_generators = []
for gen_pair in params['generator']:
    for gen_key in gen_pair.keys():
        working_path = gen_key
        gen_value = gen_pair[gen_key]
        script_with_parameters = ''
        is_valid = False
        if gen_value != None:
            for value in gen_value:
                for v_key in value.keys():
                    script = ''
                    script_name = ''
                    if v_key =='bash':
                        bash_str = ''
                        if value[v_key] != None:
                            script_name = value[v_key]
                            script = script_name
                            is_valid = True
                    elif v_key == 'script':
                        if value[v_key] != None:
                            try:
                                script_name = value[v_key]['name']
                                script_exe = ''
                                parameter_str = ''
                                if script_name != None and script_name != '':
                                    script_ext = script_name.split('.')[-1]
                                    if script_ext == 'py':
                                        script_exe = 'python3'
                                    if script_ext == 'sh':
                                        script_exe = 'sh'
                                    try:
                                        script_parameters = value[v_key]['parameters']
                                        if script_parameters != None:
                                            for parameter in script_parameters:
                                                parameter_str += ' ' + parameter
                                        else:
                                            print('No parameters')     
                                    except Exception as e:
                                        print('Missing: ' + str(e) + ', use empty parameters')
                                    script = script_exe + ' ' + script_name + parameter_str
                                    is_valid = True
                                else:
                                    print('Script name is empty, skipped')   
                            except Exception as e:
                                print('Missing: ' + str(e) + ', skipped')
                        else:
                            print('Script is empty, skipped')
                    if script_with_parameters == '':
                        script_with_parameters = script
                    else:
                        script_with_parameters = script_with_parameters + ' && ' + script
            if is_valid:
                cluster_generators.append({os.path.join(cluster_home_path,working_path):script_with_parameters})
        else:
            print('Missing script when path is available, skipped')
            
for generators in cluster_generators:
    for working_path in generators.keys():
        # print('cd ' + working_path + '; python3 ' + generators[working_path])
        print(cmd_generator(working_path,generators[working_path]))
        
            
                
            
            
            