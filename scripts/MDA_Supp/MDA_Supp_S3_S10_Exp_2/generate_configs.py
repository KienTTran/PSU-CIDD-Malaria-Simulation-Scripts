# import the regex module
import re
import os 
from pathlib import Path
import numpy as np
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

    template = (r"cmd.template")   
    all_value_list = []  
    
    # #Calculate beta log10
    start = math.log10(params['beta'][0])
    stop = math.log10(params['beta'][1])
    step = (stop - start)/params['beta'][-1]
    log10_beta = np.arange(start,stop,step)
    betas = 10**log10_beta
    params['beta'] = betas
    #kappa
    kappa_temp = np.arange(params['kappa'][0],params['kappa'][1],params['kappa'][2])
    params['kappa'] = kappa_temp
    #z
    z_temp = np.arange(params['z'][0],params['z'][1],params['z'][2])
    params['z'] = z_temp
    
        
    #generate YML
    stream = open('input_base.yml', 'r');
    data = yaml.full_load(stream);
    stream.close();
    
    location_info =  [[0, 0, 0]]
    number_of_locations = len(location_info);
    data['location_db']['location_info'] = location_info;
    data['location_db']['population_size_by_location'] = [params['population'][-1]]
        
    config_list = []
    for z in params['z']:
        for k in params['kappa']:
            for beta in params['beta']:
                new_data = copy.deepcopy(data)
                new_data['location_db']['beta_by_location'] = np.full(number_of_locations, beta).tolist()
                new_data['immune_system_information']['immune_effect_on_progression_to_clinical'] = (float)(z)
                new_data['immune_system_information']['factor_effect_age_mature_immunity'] = (float)(k)
                
                output_filename = config_folder_name + '/sim_prmc_pop_%s_kappa_%.2f_z_%.2f_beta_%.3f.yml'%(str(params['population'][-1]),k,z,beta)
                config_list.append('sim_prmc_pop_%s_kappa_%.2f_z_%.2f_beta_%.3f.yml'%(str(params['population'][-1]),k,z,beta))
                output_stream = open(output_filename, 'w');
                yaml.dump(new_data, output_stream); 
                output_stream.close();
            
    with open(r"submit_all_jobs.template", "r") as old_file:
        with open(r"submit_all_jobs.pbs", "w") as new_file:
            for line in old_file:
                if '#YML_FILES#' in line:
                    for c_index,config in enumerate(config_list):
                        if c_index == len(config_list) - 1:
                            new_file.writelines('\"' + config + '\"\n')
                        else:
                            new_file.writelines('\"' + config + '\",\n')
                elif '#REPLICATES#' in line:
                    new_file.writelines('TO=' + str(params['replicate'][0] - 1))
                else:
                    new_file.writelines(line)
        
    # #Write to cmd.sh (for Rob queue job version)
    # for index,key in enumerate(params):
    #     print(index,key,params[key])
    #     if len(all_value_list) == 0:
    #         for value in params[key]:
    #             all_value_list.append(str(value))
    #     else:
    #         temp = []
    #         for line in all_value_list:
    #             for value in params[key]:
    #                 temp.append(line + "#" + str(value))
    #         all_value_list = temp
            
    # for index,line in enumerate(all_value_list):
    #     print(index, line)          
    # line_template = ""
    # line_out = []
    # with open(r"cmd.template", "r") as old_file:
    #     for line in old_file:
    #         line_template = line            
    # line_template = re.sub("#folder#", folder, line_template)
    # with open(r"run_cmd.sh", "w") as new_file:
    #     line_out.append("#!/bin/bash\n")
    #     line_out.append("source Scripts/%s/Schedule_Run_PRMC.sh &&\n"%(folder))
    #     for index,value_list in enumerate(all_value_list):
    #         line_temp = line_template
    #         for k_index,key in enumerate(params):
    #             if key == 'beta':
    #                     line_temp = re.sub("#"+key+"#", '%.3f'%(float)(value_list.split("#")[k_index]), line_temp)
    #             else:
    #                 line_temp = re.sub("#"+key+"#", value_list.split("#")[k_index], line_temp)
    #         # print(line_temp)
    #         if index == len(all_value_list) - 1:
    #             line_out.append(line_temp)
    #         else:
    #             line_out.append(line_temp+"\n")
    #     new_file.writelines(line_out)
            
        
    
                
            