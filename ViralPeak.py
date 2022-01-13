# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 11:06:24 2021

@author: kiera
"""

import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import time
import math

start = time.time()

#############    Required Files    ################

file_dict = {

    'Symphony_filename' : '2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx',
    'INSTINCT_MRS_filename' : '2021_10_08 INSTINCT Master Results Spreadsheet.xlsx',
    'ATACCC_MRS_filename' : '2021_10_08 ATACCC Master Result Spreadsheet.xlsx',
    'FUSION_MRS_filename' : '2021_10_08 FUSION Master Result Spreadsheet.xlsx',
    'london_MRS_filename' : '2021_10_08 ATACCC2_LONDON Master Result Spreadsheet.xlsx',
    'bolton_MRS_filename' : '2021_10_08 ATACCC2_BOLTON Master Result Spreadsheet.xlsx'

}

##########    File paths    ##########

def getDir():
    
    file = open('mac_dir.txt')
    dictionary = {}
    
    # Parse the directories text file
    for ln in file.readlines():
        
        # Format and add to dictionary
        ln = ln.strip('\n')
        ln = ln.split('\t')
        dictionary[ln[0]] = ln[1]
    
    return(dictionary)

dir_dict = getDir()


#############    The Translator    ################

def Ct_ViralLoad(x):

    # RNA copies per reaction
    x = math.exp((37.933-x)/1.418)

    # RNA copies per ml
    #x = x*((1000/150)*(25/5))
    x = x * 133.3333

    return(x)

#############    The Translator    ################


####    Step 1    ####    Get list of Symphony IDs    ####
def getSymphony(filename):

    # Identify path to file
    path = dir_dict['MRS_path'] + str(filename)

    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Symptom Scores',
                                 usecols=(fields))
    participants = participants.dropna()
    part_list = list()

    # Create a list of the IDs
    for p in participants['id_sub']:

        part_list.append(p)

    return(part_list)

symphony_ids = getSymphony(file_dict['Symphony_filename'])


####    Step 2    ####    Get Viral loads (ATACCC/INSTINCT)  ####

def getINSTINCT(filename):

    path = dir_dict['MRS_path'] + str(filename)

    fields = ['id_sub','vload_d0','vload_d4','vload_d7','vload_d14',
              'vload_d27', 'vload_3m','vload_6m']

    # Import the Viral load data from the INSTINCT MRS
    data = pd.read_excel(path,
                         sheet_name='Oroswab quantitative',
                         usecols=(fields))

    # Remove missing values
    data = data.fillna(value = 0)
    data = data.replace('.',0)

    return(data)


INSTINCT_vload_data = getINSTINCT(file_dict['INSTINCT_MRS_filename'])

def getATACCC(filename):

    path = dir_dict['MRS_path'] + str(filename)

    fields = ['id_sub','ct_dN0','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5',
              'ct_d6','ct_dN7','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11',
              'ct_d12','ct_d13','ct_d14','ct_d15','ct_d16','ct_d17','ct_d18',
              'ct_d19','ct_d20','ct_d28']

    data = pd.read_excel(path,
                         sheet_name='Ct_Values',
                         usecols=(fields))

    # These need to be reversed to 0 when the viral load data is here
    data = data.fillna(value= 10000)
    data = data.replace('.',10000)
    data = data.replace('undetected',502)
    data = data.replace('detected',501)

    return(data)

ATACCC_vload_data = getATACCC(file_dict['ATACCC_MRS_filename'])


####    Step 3    ####    Import data to dictionary    #####


def INSTINCT_Dictmaker(data):
    dictionary = {}

    # loop through the length of the dataframe
    for i in range(len(data['id_sub'])):

        loads = list()

        # Loop through each column in the dataframe
        for col in data:
            # skip the ID column
            if col =='id_sub':
                continue

            # Add load to list
            loads.append(data[col][i])

        # add list of loads to dicionary
        dictionary[data['id_sub'][i]] = loads

    return(dictionary)


instinct_vload_dict = INSTINCT_Dictmaker(INSTINCT_vload_data)

def ATACCC_Dictmaker(data):

    dictionary = {}

    # Loop through the length of the data from the MRS
    for i in range(len(data['id_sub'])):

        # Only do anytjing if the ID is present in SYMPHONY
        if data['id_sub'][i] in symphony_ids:

            scores = list()

            # Loop through each column
            for col in data:

                # Skip the ID column
                if col == 'id_sub':
                    continue

                # Append to a list
                scores.append(data[col][i])

            # Add list to dictionary
            dictionary[str(data['id_sub'][i])] = scores

    return(dictionary)

ataccc_vload_dict = ATACCC_Dictmaker(ATACCC_vload_data)

####    Step 4    ####    Get the Peak Loads and the Study days    ####

def getPeaks(inst_dictionary, ata_dict):

    # Deifne the fields of the DAYS ONLY
    instinct_fields = ['vload_d0','vload_d4','vload_d7','vload_d14',
              'vload_d27', 'vload_3m','vload_6m']

    # Define the ATACCC fields
    ataccc_fields = ['ct_dN0','ct_d0','ct_d1','ct_d2','ct_d3','ct_d4','ct_d5',
              'ct_d6','ct_dN7','ct_d7','ct_d8','ct_d9','ct_d10','ct_d11',
              'ct_d12','ct_d13','ct_d14','ct_d15','ct_d16','ct_d17','ct_d18',
              'ct_d19','ct_d20','ct_d28']
    viral_peak_dict = {}

    # Loop through the Symphony IDs
    for i in symphony_ids:

        # If the ID is from ATACCC, skip it.

        # If the participant can't be found
        if i not in (list(inst_dictionary.keys())+list(ata_dict.keys())):
            entry = {'peak_vl':'.',
                     'vl_sd':'.'}
            viral_peak_dict[i] = entry

        ## If the data is present ##
        elif i[0:3] == 'INS':

            # Isolate the list of loads
            loads = inst_dictionary[i]
            # Find the index of the load peak
            day_index = loads.index(max(loads))
            # Find the study day of the load peak
            day = instinct_fields[day_index]

            # If the max is 0, study day = '.'
            if max(loads) == 0:
                day = '.'

            # Add the data to the dictionary
            entry = {'peak_vl':max(loads),
                     'vl_sd':day}
            viral_peak_dict[i] = entry

        elif i[0:3] == 'ATA':

            ataloads = ata_dict[i]
            
            day_index = ataloads.index(min(ataloads))
            day = ataccc_fields[day_index]

            # Value missing
            if min(ataloads) == 10000:
                entry = {'peak_vl':'missing',
                         'vl_sd':'.'}
                viral_peak_dict[i] = entry
                continue
            # Value detected
            elif min(ataloads) == 501:
                entry = {'peak_vl':'detected',
                         'vl_sd':'.'}
                viral_peak_dict[i] = entry
                continue
            #Value undetected
            elif min(ataloads) == 502:
                entry = {'peak_vl':0,
                         'vl_sd':'.'}
                viral_peak_dict[i] = entry
                continue

            # Value Ct to Viral load
            entry = {'peak_vl':Ct_ViralLoad(min(ataloads)),
                     'vl_sd':day}
            viral_peak_dict[i] = entry



    return(viral_peak_dict)


peak_dict = getPeaks(instinct_vload_dict, ataccc_vload_dict)


####     Step 5    ####    Output the data as a 'csv'    ####


def getArray(dictionary):

    data = pd.DataFrame.from_dict(dictionary)

    return(data.transpose())

data = getArray(peak_dict)

data.to_csv(dir_dict['output_dir'] + 'viralpeak_output.csv')


####    Concluding Statements    ####

end = time.time()
print('==============================================')
print('Total time ellapsed: ' + str(end-start))
print('==============================================')
del data
del start
del end
