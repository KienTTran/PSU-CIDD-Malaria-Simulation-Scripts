# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import math
import copy

def read_parameters():
    params = {}
    print("Reading parameters.yml")
    with open(r'parameters.yml') as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            params[item] = doc
    return params
        
if __name__=="__main__":
    config_folder_name = "generated_inputs"
    file_path = str(Path.cwd())
    if "\\" in file_path:
        folder = file_path.split("\\")[-1]  
    else:
        folder = file_path.split("/")[-1]
    config_path = os.path.join(Path.cwd(), config_folder_name)
    if not os.path.exists(config_folder_name):
        os.mkdir(config_path)
    print("Will generate configs to folder: " + config_path)
    params = read_parameters()
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
    stream = open('sim_prmc.yml', 'r');
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
                for ifr in params['ifr']:
                    config_number += 1
                    config.append([beta, z, k, ifr])
                
    print("Total %d configs, %d runs"%(config_number,config_number * params['replicates'][0]))
    
    config_df = pd.DataFrame(config)
    config_df.columns = ['beta','z','kappa','ifr']
    
    config_df.to_csv("configs.csv",index=True,index_label="Index")
        
    df = config_df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        new_data = copy.deepcopy(data)
        new_data['location_db']['beta_by_location'] = np.full(number_of_locations, row.beta).tolist()
        new_data['mosquito_config']['interrupted_feeding_rate'] = np.full(number_of_locations, (float)(row.ifr)).tolist()
        new_data['mosquito_config']['prmc_size'] = (int)(params['prmc_size'][0])
        new_data['immune_system_information']['immune_effect_on_progression_to_clinical'] = (float)(row.z)
        new_data['immune_system_information']['factor_effect_age_mature_immunity'] = (float)(row.kappa)
        
        output_filename = config_folder_name + '/%d.yml'%(index)
        output_stream = open(output_filename, 'w')
        yaml.dump(new_data, output_stream)
        output_stream.close()   
            
    #Change job_template file
    f = open("job_template.template",'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#JOB_NAME#", params['name'] + "\n")   
    f = open("job_template.pbs",'w')
    f.write(new_file_data)
    f.close()   
            
    #Change submit_all_jobs file
    f = open("submit_all_jobs.template",'r')
    template = f.read()
    f.close()
    new_file_data = template.replace("#TOTAL_CONFIGS#",str(config_number - 1) + "\n")
    new_file_data = new_file_data.replace("#REPLICATES#",str(params['replicates'][0]) + "\n")
    f = open("submit_all_jobs.pbs",'w')
    f.write(new_file_data)
    f.close()
    
    with open(r"submit_all_jobs.template", "r") as old_file:
        with open(r"submit_all_jobs.pbs", "w") as new_file:
            for line in old_file:
                if '#TOTAL_CONFIGS#' in line:
                    new_file.writelines('TO=' + str(len(config_df) - 1) + "\n")
                elif '#REPLICATES#' in line:
                    new_file.writelines('REP=' + str(params['replicates'][0]) + "\n")                    
                else:
                    new_file.writelines(line)
            
        
    
                
            