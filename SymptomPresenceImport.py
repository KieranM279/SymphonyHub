# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 12:07:30 2021

@author: kiera
"""

import os
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import time

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

filename = '2022_01_12 SYMPHONY Master Results Spreadsheet.xlsx'

##########    File paths    ##########

def getNames(filename):
    
    # Open the file with the name conversions
    names = open(filename)
    dictionary = {}
    
    # Loop through the line of the symptom names file
    for ln in names.readlines():
        
        ln = ln.strip()
        ln = ln.split(',')
        
        # Create a dictionary of Symptom diary names Vs. Future column names
        dictionary[ln[0]] = ln[1]
        
    return(dictionary)

####    Step 1    ####    Get Score list and Presence list    ####

start = time.time()

def getList():
    
    
    # Read the '.xlsx' files into python
    fields = ['id_sub']
    scorelist = pd.read_excel(dir_dict['MRS_path'] + filename,
                              sheet_name='Raw Symptom Scores',
                              usecols=(fields))
    presencelist = pd.read_excel(dir_dict['MRS_path'] +filename,
                                 sheet_name='Symptom Presence',
                                 usecols=(fields))
    raw_score_ids = list()
    presence_list = list()
    
    # Loop through the list of IDs from both Raw Scores and Presence tabs
    for s in scorelist['id_sub']:
        raw_score_ids.append(s)
    for p in presencelist['id_sub']:
        presence_list.append(p)
    
    return(raw_score_ids, presence_list)

raw_score_ids, presence_ids = getList()

####    Step 2    ####    Import Raw Symptom Data    ####

def getRawData():
    
    symp_names = list(getNames('symptom_names.txt').values())
    
    symp_names.remove('temperature')
    symp_names.remove('gi_calc')
    symp_names.remove('cffd2gi')
    symp_names.append('cffd2g1')
    
    fields = list()
    fields.append('id_sub')
    
    # Loop through the symptom names
    for name in symp_names:
        
        # Loop through the length of days
        for i in range(-10,28):
            
            if i == -10:
                field =(name + '_DU')
                fields.append(field)
            
            # Add each day to each symptom name
            field = (name + '_d' + str(i))
            # Append to list
            fields.append(field)

    
    # Read data into a dataframe
    data = pd.read_excel(dir_dict['MRS_path'] + filename,
                         sheet_name='Raw Symptom Scores',
                         index_col=0,
                         usecols=(fields))
    
    print('Symptom Scores imported...')
    
    # Replace NAs with blanks
    data = data.fillna(value = '')
    
    return(data, symp_names)

Raw_Scores, symptom_names = getRawData()

####    Step 3    ####    Get final column names    ####

def colMaker(list_of_symptoms):
    
    col_list = list()
    
    # Loop through the list of symptoms
    for i in list_of_symptoms:
        
        # Loop through a range of 3
        for c in range(3):
            
            # Add each column name
            if c == 0:
                col_list.append(i)
            elif c == 1:
                col_list.append(i+'_onset')
            elif c == 2:
                col_list.append(i+'_end')
        
    return(col_list)

column_list = colMaker(symptom_names)

####    Step 4    ####    Make a dictioanry of symptom presence    ####

def symptomPresence():
    
    dictionary = {}
    
    # Loop through each ID in symphony
    for i in presence_ids:
        print(i)
        
        entry = {}
        entry.fromkeys(symptom_names)

        # Loop through each symptom in order
        for symptom in symptom_names:
            
            Bool = True
            scores_list = list()
            
            # Loop through eah column of that symptom
            for col in Raw_Scores:
                
                # Loop through columns for the current symptom only
                if col[0:len(symptom)] == symptom:
                    
                    # Isolate the current score
                    curr_score = Raw_Scores[col][i]
                    
                    # If the current score is not blank and greater than zero
                    if curr_score != '' and curr_score > 0:
                        
                        entry[symptom] = 'Y'
                        Bool = False
                        break
                    
                    # If only zeros or blanks add to a list
                    else:
                        scores_list.append(curr_score)
            
            # If there are any zeros in the list, Presence is a No
            if Bool and (0 in scores_list or 0.0 in scores_list):
                entry[symptom] = 'N'
            
            # If the entire list is blanks, Presence is blank
            elif Bool and all(item == '' for item in scores_list):
                entry[symptom] = 'ND'
        
        # Add the entry of symptoms to the dictionary
        dictionary[i] = entry

    return(dictionary)

Presence_dict = symptomPresence()

####    Step 4    ####    Input those fucking dots    ####

def dotFiller(orig_dict):
    
    # Isolate the dict keys
    ids = list(orig_dict.keys())
    # Create a copy of the dictionary to work from
    new_dict = orig_dict
    
    # Loop through the participant IDs
    for i in ids:
        
        # Isolate the individual entry
        entry = new_dict[i]
        # Isolate the keys for that entry (individual symptoms)
        symptoms = list(entry.keys())
        score_list = list()
        
        # Loop through the symptoms
        for s in symptoms:
            
            # Append each score to a list
            score_list.append(new_dict[i][s])
            
        Bool = False
        
        # If any 'Y' or 'N' are present in the list, Change Bool to TRUE
        if any(score == 'Y' for score in score_list):
            Bool = True
        elif any(score == 'N' for score in score_list):
            Bool = True
        else:
            pass
        
        # The True Bool means that
        # the blanks for that entry should be changed to dots
        if Bool:
            
            # Loop through individual symptoms for that participant
            for s in symptoms:
                
                # Change any blanks to dots
                if new_dict[i][s] == 'ND':
                    new_dict[i][s] = '.'

    return(new_dict)

Presence_dict = dotFiller(Presence_dict)


####    Step 6    ####    export to csv   ####

def getArray(dictionary):
    
    data = pd.DataFrame.from_dict(dictionary)
    
    return(data.transpose())

data = getArray(Presence_dict)

data.to_csv(dir_dict['output_dir'] + 'presence_output.csv')

end = time.time()
print('Total time ellapsed: ' + str(end-start))
del start
del end