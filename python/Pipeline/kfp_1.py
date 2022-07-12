from kfp import dsl, compiler
import kfp.components as comp
import kfp

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

web_downloader_op = kfp.components.load_component_from_url(
    'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/contrib/web/Download/component.yaml')

pipeline_config_url = 'https://raw.githubusercontent.com/KienTTran/PSU-CIDD-Malaria-Simulation-Scripts/master/python/Pipeline/pipeline.yml'
ssh_key_url = ''

def build(pipeline_config: comp.InputArtifact(),
          ssh_key: comp.InputArtifact()):
    import paramiko
    import yaml
    import os
    from os.path import exists
    from getpass import getpass

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
        
    client = PipelineClient()
    print(pipeline_config)
    params = client.read_parameters(pipeline_config)
    print(params)
    ssh, sftp = client.connect(params['ssh']['address'], params['ssh']['username'],ssh_key)
    client.run_cmd_remotely('ls -l')

def build_pipeline():
    build_op = comp.create_component_from_func(
        func = build,
        output_component_file='component.yaml', # This is optional. It saves the component spec for future use.
        base_image='python:3.8',
        packages_to_install=['paramiko','pyaml','urllib3'])    
    pipeline_config_download_task = web_downloader_op(url = pipeline_config_url)
    ssh_key_download_task = web_downloader_op(url = ssh_key_url)
    build_op(pipeline_config = pipeline_config_download_task.outputs['data'], 
             ssh_key = ssh_key_download_task.outputs['data'])
    
args = {'url' : pipeline_config_url}
client.create_run_from_pipeline_func(build_pipeline, arguments={})