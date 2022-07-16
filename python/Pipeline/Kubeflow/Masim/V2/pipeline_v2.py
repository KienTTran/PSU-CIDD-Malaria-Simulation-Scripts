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
                                                                                ('remote_dirs', list),
                                                                                ('remote_files', list),
                                                                                ('remote_generators', list)
                                                                                ]):
    import yaml
    import os
    from collections import namedtuple
    
    print('Parsing pipeline')
    
    params = 0
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
            
    remote_username = params['ssh']['username']
    remote_home_path = "/storage/home/" + remote_username[0] + "/" + remote_username
    
    remote_repo = []
    remote_dirs = []
    remote_files = []
    remote_generators = []
    remote_work_dirs = ['bin','output','log','script']
    remote_work_path = ''
    for pair in params['project']:
        if type(pair) == str:
            print('Project is empty')
        else:
            for p_key in pair.keys():
                if pair[p_key] == None:
                    print('Project is empty')
                else:       
                    project_path = p_key             
                    remote_work_path = pair[p_key]['run']
                    for work_dir in remote_work_dirs:
                        remote_dirs.append({remote_work_path:os.path.join(remote_home_path,os.path.join(remote_work_path,work_dir))})

                    project_repo = pair[p_key]['repo']
                    if project_repo == None:
                        print('Repo is empty')
                    else:
                        project_repo_url = pair[p_key]['repo']['url']
                        if project_repo_url == None:
                            print('Repo URL is empty')
                        else:
                            project_repo_branch = pair[p_key]['repo']['branch']
                            project_repo_git = ''
                            if project_repo_branch == None:
                                project_repo_git = project_repo_url
                            else:
                                project_repo_git = project_repo_url + ' -b ' + project_repo_branch
                            remote_repo.append({os.path.join(remote_home_path,project_path):project_repo_git})
     
    remote_work_script_path = os.path.join(os.path.join(remote_home_path,remote_work_path),remote_work_dirs[4])
    remote_work_config_path = os.path.join(os.path.join(remote_home_path,remote_work_path),remote_work_dirs[1])
    remote_files =  [
                    {remote_work_script_path : params['generator']['script']},
                    {remote_work_script_path : params['generator']['parameter']},
                    {remote_work_script_path : params['generator']['input']}
                    ]

    remote_generator =  params['generator']['script'].split('/')[-1] \
                        + ' ' + params['generator']['parameter'].split('/')[-1] \
                        + ' ' + params['generator']['input'].split('/')[-1] \
                        + ' ' + remote_work_name + '_inputs.csv' \
                        + ' ' + remote_work_config_path
                        
    remote_generators.append({remote_work_script_path : remote_generator})
                        
    remote_output = namedtuple('outputs', ['remote_repo','remote_dirs','remote_files','remote_generators'])
                
    return remote_output(remote_repo,remote_dirs,remote_files,remote_generators)

def run_on_remote_func(pipeline_config: comp.InputArtifact(),
                        ssh_key: comp.InputArtifact(),
                        remote_repo: list,
                        remote_dirs: list,
                        remote_files: list,
                        remote_generators: list
                        ):
    import paramiko
    import yaml
    import os
    
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
        
        def run_cmd_remotely(self,command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command,get_pty=True)
            for line in stdout.readlines():
                print(line)
            err = stderr.read().decode()
            if err:
                print(err)
                
        def is_dir_path_existed_remotely(self,file_path):
            is_existed = False
            try:
                self.sftp.chdir(file_path) # sub-directory exists
                print(file_path + ' exists')
                is_existed = True
            except IOError:
                print(file_path + ' does not exist')
            return is_existed
            
        def is_file_path_existed_remotely(self,file_path):
            is_existed = False
            try:
                self.sftp.stat(file_path) # sub-directory exists
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
                self.sftp.chdir(remote_directory) # sub-directory exists
            except IOError:
                dirname, basename = os.path.split(remote_directory.rstrip('/'))
                self.mkdir_nested_remotely(dirname) # make parent directories
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
    
    print('Running on cluster')
    
    params = 0    
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
    
    #ssh info
    remote_address = params['ssh']['address']
    remote_username = params['ssh']['username']
    remote_home_path = "/storage/home/" + remote_username[0] + "/" + remote_username
    print('Cluster SSH info: ' + remote_username + '@' + remote_address)
            
    for repo in remote_repo:
        for working_path in repo.keys():
            print('git clone ' + repo[working_path] + ' ' + working_path)
            
    for dirs in remote_dirs:
        for working_path in dirs.keys():
            print('mkdir nest ' + dirs[working_path])
            
    for files in remote_files:
        for working_path in files.keys():
            print('cp ' + files[working_path] + ' ' + working_path)  
            
    for generators in remote_generators:
        for working_path in generators.keys():
            print('cd ' + working_path + ' run ' + generators[working_path])
    
    
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
    
    run_on_remote_op = comp.create_component_from_func(
            func = run_on_remote_func,
            output_component_file='components/run_on_remote_comp.yaml', # This is optional. It saves the component spec for future use.
            base_image='python:3.8',
            packages_to_install=['paramiko','pyaml'])
    
    run_on_remote_task = run_on_remote_op(pipeline_config = pipeline_config_download_task.outputs['data'],
                                            ssh_key = ssh_key_download_task.outputs['data'],
                                            remote_repo = parse_pipeline_config_task.outputs['remote_repo'],
                                            remote_dirs = parse_pipeline_config_task.outputs['remote_dirs'],
                                            remote_files = parse_pipeline_config_task.outputs['remote_files'],
                                            remote_generators = parse_pipeline_config_task.outputs['remote_generators']
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
print("Reading " + 'pipeline_v2.yml')
with open('pipeline_v2.yml','r') as file:
    params =  yaml.full_load(file)

remote_username = params['ssh']['username']
remote_home_path = "/storage/home/" + remote_username[0] + "/" + remote_username

remote_repo = []
remote_dirs = []
remote_files = []
remote_generators = []
remote_work_dirs = ['bin','config','output','log','script']
remote_work_path = ''
remote_work_name = ''
for pair in params['project']:
    if type(pair) == str:
        print('Project is empty')
    else:
        for p_key in pair.keys():
            if pair[p_key] == None:
                print('Project is empty')
            else:
                project_path = p_key             
                remote_work_path = pair[p_key]['run']
                remote_work_name = remote_work_path.split('/')[-1]
                for work_dir in remote_work_dirs:
                    remote_dirs.append({remote_work_path:os.path.join(remote_home_path,os.path.join(remote_work_path,work_dir))})

                project_repo = pair[p_key]['repo']
                if project_repo == None:
                    print('Repo is empty')
                else:
                    project_repo_url = pair[p_key]['repo']['url']
                    if project_repo_url == None:
                        print('Repo URL is empty')
                    else:
                        project_repo_branch = pair[p_key]['repo']['branch']
                        project_repo_git = ''
                        if project_repo_branch == None:
                            project_repo_git = project_repo_url
                        else:
                            project_repo_git = project_repo_url + ' -b ' + project_repo_branch
                        remote_repo.append({os.path.join(remote_home_path,project_path):project_repo_git})

remote_work_script_path = os.path.join(os.path.join(remote_home_path,remote_work_path),remote_work_dirs[4])
remote_work_config_path = os.path.join(os.path.join(remote_home_path,remote_work_path),remote_work_dirs[1])
remote_files =  [
                {remote_work_script_path : params['generator']['script']},
                {remote_work_script_path : params['generator']['parameter']},
                {remote_work_script_path : params['generator']['input']}
                ]

remote_generator =  params['generator']['script'].split('/')[-1] \
                    + ' ' + params['generator']['parameter'].split('/')[-1] \
                    + ' ' + params['generator']['input'].split('/')[-1] \
                    + ' ' + remote_work_name + '_inputs.csv' \
                    + ' ' + remote_work_config_path
                    
remote_generators.append({remote_work_script_path : remote_generator})
            
            