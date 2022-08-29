import os 
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import copy
import sys
import subprocess
import json

def read_parameters(parameter):
    params = {}
    print("Reading " + parameter)
    with open(parameter,'r') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    auth_info = json.loads(sys.argv[1].replace("\'", "\""))
    sim_info = json.loads(sys.argv[2].replace("\'", "\""))
    tar_info = json.loads(sys.argv[3].replace("\'", "\""))
    task_name = str(sys.argv[4])
    task_script_path = str(sys.argv[5]) 
    print(auth_info)
    print(sim_info)  
    print(tar_info)  
    
    parameter_file = str(sys.argv[6])
    input_template_file = str(sys.argv[7]) 
    job_template_file = str(sys.argv[8])
    submit_template_file = str(sys.argv[9])
    
    username = ''
    job_name = ''
    job_exe = ''
    job_name = sim_info['work_path'].split('/')[-2] + '_' + sim_info['work_path'].split('/')[-1]
    if len(job_name) >= 16:
        job_name = sim_info['work_path'].split('/')[-2][0:7] + '_' + sim_info['work_path'].split('/')[-1][-7:]
        
    username = auth_info['ssh_username']
    job_exe = sim_info['build_bin'].split('/')[-1]
    print('Generating inputs for ' + str(job_name))

    input_path = ''
    input_folder = 'input'
    if task_script_path == 'None':        
        input_path = os.path.join(os.path.dirname(os.getcwd()), input_folder)
    else:
        input_path = os.path.join(sim_info['work_path'], input_folder)
    print("Will generate configs to folder: " + input_path)
    if not os.path.exists(input_folder):
        os.makedirs(input_path, exist_ok=True)
        print("Created folder: " + input_path)
    else:
        print("Cleaning old files in folder: " + input_folder)
        subprocess.call('rm -rf ' + input_folder, shell=True)
        os.makedirs(input_path, exist_ok=True)
    params = read_parameters(parameter_file)    
        
    for p_key in params:
        if type(params[p_key]) == str and '(' in params[p_key] and ')' in params[p_key]:
            p_values = params[p_key].replace('(','').replace(')','').split(',')
            p_start = (float)(p_values[0])
            p_stop = (float)(p_values[1])
            p_total = p_values[2]
            p_step = 0.0
            
            if float(p_total) == 0.0:
                print(p_key + ' range or step cannot be zero')
                exit(0)            
            if '.' not in p_total:                
                p_step = (float)((p_stop - p_start)/(int)(p_total))
            else:
                p_step = (float)(p_total)
                
            if p_key == 'beta':
                log10_beta = np.arange(p_start,p_stop,p_step)
                betas = 10**log10_beta
                params['beta'] = betas           
            params[p_key] = np.arange(p_start,p_stop,p_step)
                    
    all_value_list = []
    all_value_columns = []
    for index,key in enumerate(params):
        print(key,params[key])
        if type(params[key]) == list or type(params[key]) == np.ndarray:
            all_value_columns.append(key)
            if len(all_value_list) == 0:
                for value in params[key]:
                    final_value = value
                    if type(value) == float:
                        final_value = '%.5f' % value
                    all_value_list.append(str(final_value))
            else:
                temp = []
                for line in all_value_list:
                    for value in params[key]:
                        final_value = value
                        if type(value) == float:
                            final_value = '%.5f' % value
                        temp.append(line + "#" + str(final_value))
                all_value_list = temp
                
    input_df = pd.DataFrame()
    inputs = []
    for index,line in enumerate(all_value_list):
        inputs.append(line.split('#'))
     
    csv_file = 'inputs.csv'  
    input_df = pd.DataFrame(inputs)
    input_df.columns = all_value_columns
    input_df.to_csv(os.path.join(input_path,csv_file),index=True,index_label="Index")        
    input_df = input_df.reset_index()  # make sure indexes pair with number of rows
    print("Total %d inputs, %d runs"%(len(input_df),len(input_df) * params['replicate'])) 
    
    #generate YML
    stream = open(input_template_file, 'r');
    data = yaml.full_load(stream);
    stream.close();
    
    try:    
        '''Edit code below this line, input_df is Dataframe of parameters'''
        location_info =  [[0, 0, 0]]
        number_of_locations = len(location_info);
        data['location_db']['location_info'] = location_info;
        data['location_db']['population_size_by_location'] = [params['population']]
        data['starting_date'] = str(params['start_year']) +'/1/1';
        data['ending_date'] = str(params['end_year']) + '/1/1';
        data['start_of_comparison_period']= str(params['start_year'])+'/1/1'; 
        for index, row in input_df.iterrows():
            new_data = copy.deepcopy(data)
            new_data['location_db']['beta_by_location'] = np.full(number_of_locations, (float)(row.beta)).tolist()
            new_data['mosquito_config']['interrupted_feeding_rate'] = np.full(number_of_locations, (float)(row.ifr)).tolist()
            new_data['mosquito_config']['prmc_size'] = (int)(row.prmc_size)
            new_data['immune_system_information']['immune_effect_on_progression_to_clinical'] = (float)(row.z)
            new_data['immune_system_information']['factor_effect_age_mature_immunity'] = (float)(row.kappa)
            new_data['location_db']['p_treatment_for_less_than_5_by_location'] = np.full(number_of_locations, (float)(row.treatment)).tolist()
            new_data['location_db']['p_treatment_for_more_than_5_by_location'] = np.full(number_of_locations, (float)(row.treatment)).tolist()
            
            '''Edit code above this line, do not edit below code'''
            output_file_path = os.path.join(input_path,'%d.yml'%(index))
            output_stream = open(output_file_path, 'w')
            yaml.dump(new_data, output_stream)
            output_stream.close()
            
        #Change job_template file
        f = open(job_template_file,'r')
        template = f.read()
        f.close()
        new_file_data = template.replace("#JOB_NAME#", job_name + "\n")
        new_file_data = new_file_data.replace("#JOB_EXE#", job_exe + "\n")        
        f = open(job_template_file,'w')
        f.write(new_file_data)
        f.close()            
        	
        #Change submit_all_jobs file
        f = open(submit_template_file,'r')
        template = f.read()
        f.close()
        new_file_data = template.replace("#JOB_NAME#", job_name + "\n")
        new_file_data = new_file_data.replace("#USERNAME#",username + "\n")
        new_file_data = new_file_data.replace("#TOTAL_INPUTS#",str(len(input_df) - 1) + "\n")
        new_file_data = new_file_data.replace("#REPLICATES#",str(params['replicate']) + "\n")
        f = open(submit_template_file,'w')
        f.write(new_file_data)
        f.close()
        
    except Exception as e:
        print("Generate input error " + str(e) + ', please check and rerun')
        exit(0)