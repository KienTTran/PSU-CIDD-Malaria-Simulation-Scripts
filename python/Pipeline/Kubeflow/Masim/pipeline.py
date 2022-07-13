from kfp import dsl, compiler
import kfp.components as comp
import kfp
from typing import NamedTuple

client = kfp.Client(host='http://172.28.86.153:31492/')
print(client.list_experiments())

download_op = kfp.components.load_component_from_url(
'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/contrib/web/Download/component.yaml')

pipeline_config_url = \
''

ssh_key_url = \
''

def run_on_cluster_func(pipeline_config: comp.InputArtifact(),
                        ssh_key: comp.InputArtifact()):
    import paramiko
    import yaml
    import os
    
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
    
    client = PipelineClient()
    
    #ssh info
    cluster_address = params['ssh']['address']
    cluster_username = params['ssh']['username']
    cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
    print('Cluster SSH info: ' + cluster_username + '@' + cluster_address)
    
    '''Connect to server '''
    ssh, sftp = client.connect(params['ssh']['address'], params['ssh']['username'],ssh_key)
    client.run_cmd_remotely('ls -l')  
    
    
def generate_build_script_func(pipeline_config: comp.InputArtifact(),
                              generate_template: comp.InputArtifact(),
                              generated_script_path: comp.OutputPath()):    
    import yaml
    
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

    params = 0
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
            
    #Script info
    generate_build_script(generate_template, params['ssh']['username'], generated_script_path)

def upload_config_generator_func(pipeline_config: comp.InputArtifact()):
    import yaml
    import os
    
    params = 0
    print("Reading " + pipeline_config)
    with open(pipeline_config,'r') as file:
        params =  yaml.full_load(file)
        
    generator_parameters = params['upload']['generator']['parameters']
    generator_parameter_str = ''
    if generator_parameters != None:
        for parameter in generator_parameters:
            generator_parameter_str += ' ' + str(parameter)
    
    cluster_username = params['ssh']['username']
    cluster_home_path = "/storage/home/" + cluster_username[0] + "/" + cluster_username
    upload_file_pairs = params['upload']['remote']['files']
    cluster_upload_file_path = []
    cluster_upload_mkdir_path = []
    for pair in upload_file_pairs:
        if type(pair) == str:
            cluster_upload_mkdir_path.append(os.path.join(cluster_home_path,pair))
        else:
            for key in pair.keys():
                upload_path = key
                upload_files = pair[key]
                cluster_upload_mkdir_path.append(os.path.join(cluster_home_path,upload_path))
                for upload_file in upload_files:
                    cluster_file_path = os.path.join(os.path.join(cluster_home_path,upload_path),upload_file)
                    cluster_upload_file_path.append(cluster_file_path)
                    print(upload_file + ' --> ' + cluster_file_path)
    
def pipeline():        
    pipeline_config_download_task = download_op(url = pipeline_config_url)
    ssh_key_download_task = download_op(url = ssh_key_url)
    
    # upload_config_generator_op = comp.create_component_from_func(
    #         func = upload_config_generator_func,
    #         output_component_file='components/upload_config_generator_comp.yaml',
    #         base_image='python:3.8',
    #         packages_to_install=['pyaml'])
    
    # upload_config_generator_task = upload_config_generator_op(pipeline_config = pipeline_config_download_task.outputs['data'])
    
    # generate_build_script_op = comp.create_component_from_func(
    #         func = generate_build_script_func,
    #         output_component_file='components/generate_script_comp.yaml',
    #         base_image='python:3.8',
    #         packages_to_install=['pyaml'])
    
    # generate_build_script_task = generate_build_script_op(pipeline_config = pipeline_config_download_task.outputs['data'],
    #                                                       generate_template = build_generate_template_download_task.outputs['data'])
    
    # run_on_cluster_op = comp.create_component_from_func(
    #         func = run_on_cluster_func,
    #         output_component_file='components/run_on_cluster_comp.yaml', # This is optional. It saves the component spec for future use.
    #         base_image='python:3.8',
    #         packages_to_install=['paramiko','pyaml'])
    
    # run_on_cluster_task = run_on_cluster_op(pipeline_config = pipeline_config_download_task.outputs['data'],
    #                                         ssh_key = ssh_key_download_task.outputs['data'])
    

#%%
client.create_run_from_pipeline_func(pipeline, arguments={})

    #%%
if __name__ == '__main__':
    # Compiling the pipeline
    kfp.compiler.Compiler().compile(pipeline, __file__ + '.yaml')