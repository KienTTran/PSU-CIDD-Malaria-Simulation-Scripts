from kfp import dsl, compiler
import kfp.components as comp
import kfp
from typing import NamedTuple

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

download_op = kfp.components.load_component_from_url(
'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/contrib/web/Download/component.yaml')

pipeline_config_url = \
'https://raw.githubusercontent.com/KienTTran/PSU-CIDD-Malaria-Simulation-Scripts/master/python/Pipeline/pipeline.yml'

ssh_key_url = \
''

build_script_url = \
'https://raw.githubusercontent.com/KienTTran/PSU-CIDD-Malaria-Simulation-Scripts/master/python/Pipeline/build/generate_build_scripts.py'

build_template_url = \
'https://raw.githubusercontent.com/KienTTran/PSU-CIDD-Malaria-Simulation-Scripts/master/python/Pipeline/build/build.template'
      
def build_func(pipeline_config: comp.InputArtifact(),
          ssh_key: comp.InputArtifact(),
          script: comp.InputArtifact(),
          template: comp.InputArtifact()) ->  NamedTuple('outputs', [
                                                        ('exe_path', str)
                                                        ]):
    
    import paramiko
    import yaml
    import os
    from os.path import exists
    from collections import namedtuple
                
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

    def generate_build_script(template_file, 
                              username, 
                              sh_script_path):       
        f = open(template_file,'r')
        temp = f.read()
        f.close()
        build_sh_file_data = temp.replace("#username#",username)
        print('Writing build script username: ' + str(username))
        f = open(sh_script_path,'w')
        f.write(build_sh_file_data)
        f.close()

    class PipelineClient():
        ssh = paramiko.SSHClient()
        sftp = 0
        
        def read_parameters(self, input_yaml):
            print("Reading " + input_yaml)
            with open(input_yaml,'r') as file:
                return yaml.full_load(file)
        
        def disconnect(self):
            self.ssh.close()
            self.sftp.close()
            
        def run_cmd_locally(self,command):
            print("[Local] >>> ", command)
            try:
                os.system(command)
            except Exception as e:
                print('Run cmd locally with error ' + str(e))
                exit(0)
        
        def run_cmd_remotely(self,command):
            print("[Remote] >>> ", command)
            (stdin, stdout, stderr) = self.ssh.exec_command(command,get_pty=True)
            for line in stdout.readlines():
                print(line)
            err = stderr.read().decode()
            if err:
                print(err)
                
        def print_path_exist_locally(self,file_path):
            if exists(file_path):
                print(file_path + ' exists')
            else:
                print(file_path + ' does not exist')
                
        def print_dir_path_exist_remotely(self,file_path):
            try:
                self.sftp.chdir(file_path) # sub-directory exists
                print(file_path + ' exists')
                return True
            except IOError:
                print(file_path + ' does not exist')
                return False
            
        def print_file_path_exist_remotely(self,file_path):
            try:
                self.sftp.stat(file_path) # sub-directory exists
                print(file_path + ' exists')
                return True
            except IOError:
                print(file_path + ' does not exist')
                return False
                
        def mkdir_nested(self, remote_directory):
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
        
    '''Pipeline start'''
    client = PipelineClient()
    params = client.read_parameters(pipeline_config)
    print(params)
        
    #ssh info
    cluster_address = params['ssh']['address']
    cluster_username = params['ssh']['username']
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

    generate_build_script(template, params['ssh']['username'], script_name)

    print('Local build script path: ' + script_name)
    print('Cluster build script path: ' + cluster_script_path) 
    
    '''Connect to server '''
    ssh, sftp = client.connect(params['ssh']['address'], params['ssh']['username'],ssh_key)
    client.run_cmd_remotely('ls -l')   
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
    sftp.put(script_name, cluster_script_path)    
    client.run_cmd_remotely(cmd_build(cluster_project_path,script_name,script_parameter_str))
        
    pipeline_output = namedtuple('outputs', ['exe_path'])
    if client.print_file_path_exist_remotely(cluster_target_path):
        return pipeline_output(cluster_target_path)    

  
def pipeline():
    build_op = comp.create_component_from_func(
        func = build_func,
        output_component_file='component.yaml', # This is optional. It saves the component spec for future use.
        base_image='python:3.8',
        packages_to_install=['paramiko','pyaml'])
        
    pipeline_config_download_task = download_op(url = pipeline_config_url)
    ssh_key_download_task = download_op(url = ssh_key_url)    
    build_script_download_task = download_op(url = build_script_url)
    build_template_download_task = download_op(url = build_template_url)
    
    build_task = build_op(pipeline_config = pipeline_config_download_task.outputs['data'], 
             ssh_key = ssh_key_download_task.outputs['data'],
             script = build_script_download_task.outputs['data'],
             template = build_template_download_task.outputs['data'])
    

#%%
client.create_run_from_pipeline_func(pipeline, arguments={})

    #%%
if __name__ == '__main__':
    # Compiling the pipeline
    kfp.compiler.Compiler().compile(pipeline, __file__ + '.yaml')