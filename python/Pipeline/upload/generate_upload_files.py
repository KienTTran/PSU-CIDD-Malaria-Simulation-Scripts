# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import math
import copy
import sys

def read_parameters(parameter):
    params = {}
    print("Reading " + parameter)
    with open(parameter,'r') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    config_folder = str(sys.argv[1])
    parameter_file = str(sys.argv[2])
    config_file = str(sys.argv[3])
    username = str(sys.argv[4])
    job_name = str(sys.argv[5])
    job_template_file = str(sys.argv[6])
    submit_job_template_file = str(sys.argv[7])
    job_exe = 'MaSim'
    csv_file = 'configs.csv'
    
    file_path = str(Path.cwd())
    if "\\" in file_path:
        folder = file_path.split("\\")[-1]  
    else:
        folder = file_path.split("/")[-1]
    config_path = os.path.join(Path.cwd(), config_folder)
    if not os.path.exists(config_folder):
        os.mkdir(config_path)
    print("Will generate configs to folder: " + config_path)
    params = read_parameters(parameter_file)
    print(params)
     
    #Calculate beta log10
    start = math.log10(params['beta'][0])
    stop = math.log10(params['beta'][1])
    step = (stop - start)/params['beta'][-1]
    log10_beta = np.arange(start,stop,step)
    betas = 10**log10_beta
    params['beta'] = betas
    #kappa
    params['kappa'] = np.arange(params['kappa'][0],params['kappa'][1],params['kappa'][2])
    #z
    params['z'] = np.arange(params['z'][0],params['z'][1],params['z'][2])
        
    #generate YML
    stream = open(config_file, 'r');
    data = yaml.full_load(stream);
    stream.close();
    
    location_info =  [[0, 0, 0]]
    number_of_locations = len(location_info);
    data['location_db']['location_info'] = location_info;
    data['location_db']['population_size_by_location'] = [params['population'][-1]]
    # data['initial_strategy_id'] = params['therapy_id'][-1]    
    data['starting_date'] = str(params['start_year'][-1])+'/1/1';
    data['ending_date'] = str(params['end_year'][-1])+'/1/1';
    data['start_of_comparison_period']= str(params['start_year'][-1])+'/1/1';   
  
    config_df = pd.DataFrame()
    config = []
    config_number = 0
    for beta in params['beta']:
        for z in params['z']:
            for k in params['kappa']:                
                config_number += 1
                config.append([beta, z, k])
                
    print("Total %d configs, %d runs"%(config_number,config_number * params['replicates'][0]))
    
    config_df = pd.DataFrame(config)
    config_df.columns = ['beta','z','kappa']
    
    config_df.to_csv(csv_file,index=True,index_label="Index")
        
    df = config_df.reset_index()  # make sure indexes pair with number of rows
    try:
        for index, row in df.iterrows():
            new_data = copy.deepcopy(data)
            new_data['location_db']['beta_by_location'] = np.full(number_of_locations, row.beta).tolist()
            new_data['mosquito_config']['interrupted_feeding_rate'] = np.full(number_of_locations, params['ifr'][0]).tolist()
            new_data['mosquito_config']['prmc_size'] = (int)(params['prmc_size'][0])
            
            output_filename = config_folder + '/%d.yml'%(index)
            output_stream = open(output_filename, 'w')
            yaml.dump(new_data, output_stream)
            output_stream.close()
    except Exception as e:
        print("Generate input error " + str(e) + ', please check and rerun')
        exit(0)
        
    #Change job_template file
    f = open(job_template_file,'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#JOB_NAME#", job_name + "\n")
    new_file_data = new_file_data.replace("#JOB_EXE#", job_exe + "\n")
    
    f = open(job_template_file.replace('.template','.pbs'),'w')
    f.write(new_file_data)
    f.close()            
    	
    #Change submit_all_jobs file
    f = open(submit_job_template_file,'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#USERNAME#",username + "\n")
    new_file_data = new_file_data.replace("#TOTAL_CONFIGS#",str(len(config_df) - 1) + "\n")
    new_file_data = new_file_data.replace("#REPLICATES#",str(params['replicates'][0]) + "\n")
    f = open(submit_job_template_file.replace('.template','.pbs'),'w')
    f.write(new_file_data)
    f.close()
            
    #Zip output folders:
    file_count = len([name for name in os.listdir(config_folder) if os.path.isfile(os.path.join(config_folder, name))])
    if file_count == config_number:
        print("Zipping genereted configs folder")
        os.system('tar -cvf ' + config_folder + '.tar.gz' + ' ' + config_folder)
    else:
        print("Error in generating configs, not enough files, pelase check and rerun")
        exit(0)
    
    
    
            
        
    
                
            