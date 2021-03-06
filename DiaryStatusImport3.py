# -*- coding: utf-8 -*-
"""
Created on Mon May 17 11:40:56 2021

@author: kiera
"""

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

########    Required paths    ########

########    Required filenames    ########

symphony_filename = '2021_10_25 SYMPHONY Master Results Spreadsheet.xlsx'

########    Required filenames    ########

####    Pre-requisite function    ####

def MotifF(motif,string):
    
    # Sets the length of the motif and string
    motif_length = len(motif)
    string_length = len(string)
    
    # Loops as a sliding windos through the String
    for i in range(string_length):
        
        # Potential match to motif
        P_match = string[i:i+motif_length]
        
        # Conditional identifying the presence of the motif
        if len(P_match) < motif_length:
            break
        elif motif == P_match:
            Bool = True
            break
        else:
            Bool = False
    
    return(Bool)


####    Step 1    ####    Get a list of participant IDs from Symphony    ####

def getSymphony(filename):
    
    
    path = str(dir_dict['MRS_path'] + symphony_filename)
    
    # Import the relevent data from the Symphony spreadsheet
    fields = ['id_sub']
    data = pd.read_excel(path,
                         sheet_name='Diary Status',
                         usecols=(fields))
    
    id_list = list()
    
    # Loop through data and append IDs to a list
    for i in data['id_sub']:
        id_list.append(i)

    return(id_list)

participant_ids = getSymphony('symphony.xlsx')


####    Step 2    ####  Create a dictionary of participant SD filenames  ####

def DiaryDictmaker():
    dictionary = {}
    
    # Get a list of filenames from the TRACKER DATABASE
    ataccc_diary_list = os.listdir(dir_dict['ataccc_symptom_diaries'])
    
    instinct_diary_list = os.listdir(dir_dict['instinct_symptom_diaries'])
    
    ####    INSTINCT Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameINS in instinct_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameINS[0:3] != 'INS':
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameINS[0:7])] = filenameINS
        
        if str(filenameINS[7]) == 'i':
            dictionary[str(filenameINS[0:8])] = filenameINS
    
    ####    ATACCC Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameATA in ataccc_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameATA[0:3] != 'ATA':
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameATA[0:7])] = filenameATA
        
        if str(filenameATA[7]) == 'i':
            dictionary[str(filenameATA[0:8])] = filenameATA
    
    return(dictionary)

diary_dict = DiaryDictmaker()

####    Step 3    ####    Find all the up until wells    ####

def getWellSoon(filenames_dict):
    
    ids_with_filenames = list(filenames_dict.keys())
    dictionary = {}
    
    for i in participant_ids:
    
        #if i[0:3] == 'INS':
        #    dictionary[i] = ''
        #    continue
        if i not in ids_with_filenames:
            dictionary[i] = 'no file'
            continue
        elif MotifF('well', filenames_dict[i]):
            dictionary[i] = 'Y'
        elif MotifF('issing', filenames_dict[i]):
            dictionary[i] = 'Symptom Diary Missing'
        elif len(filenames_dict[i]) == 12:
            dictionary[i] = 'kieran_is_slow'
        else:
            dictionary[i] = 'N'
        
    return(dictionary)

wellness_dict = getWellSoon(diary_dict)


####    Step 4    ####    Import the new Symptoms names    ####

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

# Create a list of the new file names
symptoms = list(getNames('symptom_names.txt').values())

####    Step 5    ####    Function to import entire symptom diaries    ####

def getData(filename):
    
    if filename[0:3] == 'INS':
        
        ###   INSTINCT   ###
        path = str(dir_dict['instinct_symptom_diaries'] + filename)
        
    elif filename[0:3] == 'ATA':
        
        ###   ATACCC   ###
        path = str(dir_dict['ataccc_symptom_diaries']  + filename)
    
    
    # Read the '.xlsx' file into python
    data = pd.read_excel(path,
                         sheet_name='SYMPTOM_DIARY',
                         header=1,
                         index_col=(0),
                         skiprows=([2,4]),
                         #skipfooter=35
                         )
    # Isolate the rows you want
    data = data[:31]
    
    # Get the improved row names from Step 1
    data2 = data.set_axis(symptoms)
    
    # Replace all the values I need replacing
    data2 = data2.fillna(value = '')
    data2 = data2.astype('str')
    data2 = data2.replace('NaT','')
    data2 = data2.replace('Y', 1.5)
    data2 = data2.replace('N', 0)
    data2 = data2.replace('Y - Mild', 1)
    data2 = data2.replace('Y - Moderate', 2)
    data2 = data2.replace('Y - Severe', 3)
    
    ###  Remove eroneous zeroes in the scores section ###
    
    # Isolate the symptom portion of the dataframe
    symptoms_df = data2[0:23]
    cols_to_change = list()
    
    # Loop through each day of the symptoms only dataframe
    for d in symptoms_df:
        
        # Create a list of the the symptom data for the current day
        my_list = list(symptoms_df[d])
        
        # If all of the items in the list are strings (e.g. '')
        if(all(isinstance(item, str) for item in my_list)):
            
            # Add the day to a list
            cols_to_change.append(d)
    
    # Loop through the columns that need changing
    for c in cols_to_change:
        
        # Create an empty list of strings (length 0)
        empty_list = list()
        for blank in range(31):
            empty_list.append('')
        
        # Add that empty list to the original dataframe
        data2[c] = empty_list
    
    return(data2)

#diary = getData('ATA0025 up to being well.xlsx')


####    Step 6    #### Re-organises dataframe into a dictionary format ####

def reorgData(df):
    
    a = 'fluff'
    days_dict = {}
    symptoms_dict = {}
    
    # Loop through each day in the data frame
    for i in df:
        
        # If the diary goes past Day 27, ignore it
        if str(i[0:3]) == 'Unn' and a[-2:] == str(27):
            continue
        
        # Add each day of scores to the dictionary
        days_dict[str(i)] = list(df[i])
        
        a = i
    
    ## Create the dictionary of scores by symptom
    
    # Setup new day range
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    counter = 0 # Counts the days in the symptom diary
    
    # Loop through each symptom
    for s in symptoms:
        
        symp_scores = list()
        
        # Loop through the all days of that symptom (new_days)
        for d in range(len(new_days)):
            
            curr_day = new_days[d]
            
            # If the current day is not in the symptom diary
            if str(curr_day) not in list(days_dict.keys()):
                
                # Append a blank string
                symp_scores.append('')
            
            elif str(curr_day) in list(days_dict.keys()):
                
                # Else, add the score from the symptom diary
                score = days_dict[curr_day][counter]
                symp_scores.append(score)
                
        counter += 1
        
        # Then add the scores to the dictionary
        symptoms_dict[s] = symp_scores
    
    final_dict = {}
    
    for x, day in enumerate(new_days):
        
        #print(x, day)
        
        keys = symptoms_dict.keys()
        scores_list = list()
        
        for symp in keys:
            scores_list.append(symptoms_dict[symp][x])
        
        final_dict[day] = scores_list
    
    
    return(final_dict)


#data_dict = reorgData(diary)


####    Step 7    ####    Get the End day of the symptom diary    ####

def getOmega(part_diary_dict):
    
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    for i, day in enumerate(reversed(new_days)):
        
        scores = part_diary_dict[day]
        
        if(all(isinstance(item, str) for item in scores) and day=='DAY -10*'):
            end = ''
            continue
        elif(all(isinstance(item, str) for item in scores)):
            continue
        else:
            end = day
            break
    
    return(end)
        
#getOmega(data_dict)
    
####    Step 8    ####    Get the start day of the Symptom Diary    ####

def getAlpha(part_diary_dict):
    
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    for i, day in enumerate(new_days):
        
        scores = part_diary_dict[day]
        
        if(all(isinstance(item, str) for item in scores) and day == 'DAY 27'):
            start = ''
            continue
        elif(all(isinstance(item, str) for item in scores)):
            continue
        else:
            start = day
            break
    
    return(start)

#getAlpha(data_dict)


####    Step 9    #### Make and Dictionary of Diary Start and End days ####

def AlphaOmegaDictmaker():
    dictionary = {}
    for i in participant_ids:

        print(i)
        entry = {'start':'',
                 'end':''}
        if i not in list(diary_dict.keys()):
            start = ''
            end = ''
        else:
            filename = diary_dict[i]
            data = getData(filename)
            data_dict = reorgData(data)
            start = getAlpha(data_dict)
            end = getOmega(data_dict)
          
        entry['start'] = start.strip('*')
        entry['end'] = end.strip('*')
        dictionary[i] = entry
    
    return(dictionary)
            

AlphaOmega_dict = AlphaOmegaDictmaker()



####    Step 10    ####    Export data to a '.csv' file    ####


def getArray():
    
    # The main dictionary of dictionaries
    dictionary = {}
    
    for i in participant_ids:
    
        # The dictionary entry layout for each participant
        dictionary_entry = {'id_sub':str(i),
                            'collection_method':'',
                            'diary_sd_start':AlphaOmega_dict[i]['start'],
                            'diary_sd_end':AlphaOmega_dict[i]['end'],
                            'up_to_well':str(wellness_dict[i]),
                            'up_to_withdraw':'',
                            'interruption':''}
        
        dictionary[i] = dictionary_entry
    
    data = pd.DataFrame(dictionary)
    return(data.transpose())

data = getArray()

data.to_csv(dir_dict['output_dir'] + 'diary_status_output.csv')   

end = time.time()

print('========================================')
print("Time to import Diary Statuses:")
print(str(end-start))
print('========================================')