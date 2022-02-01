#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 14:38:17 2022

@author: kieran
"""

# script for finding grouped symptom presence


symphony_filename = '2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx'


import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import time

start = time.time()


########    Required paths    ########

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


#### Create a dictionary of all symptoms groups ####

def getGroups():
    
    # Import data from relevant files
    file = open('symptom_groups.txt')
    all_symptoms = open('symptom_names_redux.txt')
    dictionary = {}
    all_symp = list()
    
    # Loop through lines of grouped symptoms
    for ln in file.readlines():
        
        ln = ln.split()
        dictionary[ln[0]] = ln[1:len(ln)]
    
    # Loop though each individual symptom
    for ln in all_symptoms.readlines():
        
        # Clean the data
        ln = ln.split()
        ln = ln[-1].split(',')
        
        # Append the symptom to a growing list
        all_symp.append(ln[-1])
    
    # Add the list of all symptoms to a dictionary
    dictionary['all'] = all_symp
    
    return(dictionary)

symptom_dict = getGroups()


####    Get a list of all the Symphony IDs    ####

def getSymphony():
   
    path = str(dir_dict['MRS_path']) + str(symphony_filename)
    
    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Grouped Symptoms',
                                 usecols=(fields))
    
    # Remove NAs and export as list
    participants = participants.dropna()
    part_list = participants['id_sub'].tolist()
    
    return(part_list)

symphony_ids = getSymphony()

#### Import all the data for the symptoms of interest ####

def importData(group):
    
    # Isolate path to Symphony
    path = dir_dict['MRS_path'] + symphony_filename
    
    # Determine what fields are to be imported
    fields = ['id_sub']
    for c in symptom_dict[group]:
        
        fields.append((c + '_DU'))
        
        for n in range(-10,28,1):
            fields.append((c + '_d' + str(n)))
    
    # Import the symptom scores
    data = pd.read_excel(path,
                         sheet_name='Raw Symptom Scores',
                         usecols=(fields),
                         index_col=(0))
    
    data = data.fillna('')
    
    return(data)
    

#### Isolate and transforms the data for a single participant into a table ####


def individualSD(df, id_sub, symptom_group):
    
    dictionary = {}
    
    # Isolate the the individual participant data
    data = df.loc[id_sub]
    data = data.to_dict()
    
    # Loop through the symptoms in the specified group
    for s in symptom_dict[symptom_group]:
        
        # Create a list datapoint keys needed for the symptom
        first = s + '_DU'
        days = [first]
        for n in range(-10,28,1):
            days.append((s + '_d' + str(n)))
        
        symptom_row = list()
        
        # Isolate the datapoints for that symptom
        # This is done janckily as a order is important
        for i in data.keys():
            for d in days:
                if i == d:
                    
                    symptom_row.append(data[i])
                    
        dictionary[s] = symptom_row
    
    return(dictionary)



#### Finding the start and end of the symptoms ####


def findAlpha(data):
    
    # Setup day range
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12', 
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    finish = False
    onset = 'never'
    
    ## Check the data for missingness ##
    
    data_check = list()
    
    # Loop through each symptoms
    for key in data.keys():
        
        #If all the data is missing for the symptom, mark as missing
        result = all(element == '' for element in data[key])
        if (result):
            data_check.append('ND')
        else:
            data_check.append('data')
    
    # If all the symptoms have missing data, mark onset as missing
    result2 = all(element == 'ND' for element in data_check)
    
    if (result2):
        onset = 'ND'
        finish = True

    
    
    # Loop through the days in the dictionary
    for d in range(39):
        
        # Test if the onset day has been found
        if finish:
            break
        
        # Lop through the symptoms in the dictionary
        for symp in data.keys():
            
            # Skip if the fields was empty
            if data[symp][d] == '':
                continue
            
            # Skip if the symptoms was not present
            elif data[symp][d] == 0:
                continue
            
            # Save the study day of onset
            else:
                onset = new_days[d]
                finish = True
                break
    
    
    # Strip day of useless data
    onset = onset.strip('DAY *')
    
    # Replace the 'D' for necassary values
    if onset == 'U':
        onset = 'DU'
    elif onset == 'N':
        onset = 'ND'
    
    return(onset)
            
            
        



def findOmega(data):
    
    # Setup day range
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    finish = False
    end = 'never'
    
    ## Check the data for being absent ##
    data_check = list()
    
    # Loop through each symptom
    for key in data.keys():
        
        # If the data is all blanks for that symptom, mark as missing
        result = all(element == '' for element in data[key])
        if (result):
            data_check.append('ND')
        else:
            data_check.append('data')
    
    # If all datapoints are missing, mark the end as no data
    result2 = all(element == 'ND' for element in data_check)
    
    if (result2):
        end = 'ND'
        finish = True
    
    
    # Loop throufh the days of the Symptom Diary
    for d in range(39):
        
        if finish:
            break
        
        # Loop though each symptoms in the participant
        for symp in data.keys():
            
            # Skip if the fields was empty
            if data[symp][d] == '':
                continue
            
            # Skip if the symptoms was not present
            elif data[symp][d] == 0:
                continue
            
            # Save the study day of end
            else:
            
                end = new_days[d]
                break
    
    
    # Strip day of useless data
    end = end.strip('DAY *')
    
    # Replace the 'D' for necassary values
    if end == 'U':
        end = 'DU'
    elif end == "N":
        end = 'ND'
    
    return(end)
            


#### Collate the data ####

def dataCollate():
    
    dictionary = {}
    fdictionary = {}
    
    # Lay out a list of the groups in order
    groups = ['all','canonical','cffd2g1','lower','upper','gi','systemic','houstons_seven']
    
    # Loop through the above groups
    for g in groups:
        
        print("Finding the onset and end of the " + g + " symptoms")
        
        # Import the data for the symptoms of that group
        data = importData(g)
        
        entry = {}
        
        # Loop through the Symphony participants
        for i in symphony_ids:
            
            if i == 'ATA0351':
                print("25% complete")
            elif i == 'INS0280':
                print("50% complete")
            elif i == 'FUZR018':
                print("75% complete")
            elif i == 'FUZR278':
                print("done")
            else:
                pass
            
            # Create a dictionary of data for each participant
            participant_data = individualSD(data, i, g)
            
            # Create column names
            a = (g + '_onset')
            o = (g + '_end')
            
            # Find the onset and end for each group
            entry[i] = {a:findAlpha(participant_data),
                        o:findOmega(participant_data)}
        
        
        dictionary[g] = entry
    
    
    # Re-organise the output dictionary for export
    for p in symphony_ids:
        
        entry = {}
        
        for symptom_group in groups:
            
            # Create column names
            a = (symptom_group + '_onset')
            o = (symptom_group + '_end')
            
            # Assign the values across the dictionaries
            entry[a] = dictionary[symptom_group][p][a]
            entry[o] = dictionary[symptom_group][p][o]
        
        fdictionary[p] = entry
            
    
    
    return(fdictionary)


final_dict = dataCollate()


####    Step 6    ####    export to csv   ####

def getArray(dictionary):
    
    data = pd.DataFrame.from_dict(dictionary)
    return(data.transpose())

data = getArray(final_dict)

data.to_csv(dir_dict['output_dir'] + 'grouped_presence_output.csv')



end = time.time()
print('Time ellapsed: ' + str((end-start)))
del start
del end
