# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 11:01:31 2021

@author: kiera
"""

import os
#os.chdir('C:/Users/kiera/Desktop/Symphony/Symptom Diary Import')
os.chdir('/Volumes/kmadon/Documents/InProgress/SymphonyHub/')
import pandas as pd
import numpy as np
from numpy import savetxt
import time
start = time.time()

#######      Path Variables required      #######

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

#######      Path Variables required      #######


####    Step 1    ####    Import the new Symptoms names    ####

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


####    Step 2    ####    Function to import the Symptom data    ####

def getData(filename):
    
    if filename[0:3] == 'INS':
        ###   INSTINCT   ###
        path = str(dir_dict['instinct_symptom_diaries'] + str(filename))
        
    elif filename[0:3] == 'ATA':
        ###   ATACCC   ###
        path = str(dir_dict['ataccc_symptom_diaries'] + str(filename))
        
        
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
    data2 = data2.replace('.','')
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

#data = getData('INS0047.xlsx')

####    Step 3    #### Re-organises dataframe into a dictionary format ####

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
    
    return(symptoms_dict)


####    Step 4    ####    Create a list of all the columns to be made    ####

def colMaker(df):
    
    # Define the three sets of columns I want to create
    column_dict = {'colset1' : ['symp'],
                   'colset2' : ['cffd2gi','lower','upper','gi','system',
                                'sburden'],
                   'colset3' : ['normal','fever','cough_persistent',
                                'cough_productive','cough_blood','breathless','muscle_aches',
                                'nausea','fatigue','confusion','diarrhoea',
                                'chest_pain','headache','sore_throat',
                                'rhinitis','rash','conjunctivitis','anosmia',
                                'hoarse_voice','appetite_loss','abdominal_pain',
                                'wheeze']}
    
    col_list = list()
    
    # Loop though each of the three column sets
    for col_set in column_dict:
        # Loop though each column within each set
        for c in column_dict[col_set]:
            # Loop through the range of study days (-10 to 27)
            for i in range(-10,28):
                
                # Create a list of column names for each column
                column = str(c + '_d' + str(i))
                col_list.append(column)
    
    # Transform list into an array
    #col_array = np.array([col_list])
    return(col_list)

#columns = colMaker(data)

#col_array  = np.array([columns])
#savetxt('Columns.csv', col_array, delimiter=',',fmt='%s')


####    Step 5    ####    Create a diary of all the diary filenames    ####

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


####    Step 6    ####    Get a list of all the Symphony IDs    ####

def getSymphony():
    
    filename = '2021_10_08 SYMPHONY Master Results Spreadsheet.xlsx'
    path = str(dir_dict['MRS_path']) + str(filename)
    
    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Symptom Scores',
                                 usecols=(fields))
    participants = participants.dropna()
    
    part_list = participants['id_sub'].tolist()
    
    return(part_list)

symphony_ids = getSymphony()


####    Step 7    ####    Collate the data    ####

def collateData():
    
    final_dict = {}
    
    # Ordered list of columns to utilise the symptom dictionary
    column_list = ['symp','cffd2gi','lower','upper','gi','system','sburden',
                   'normal','fever','cough_persistent','cough_productive',
                   'cough_blood','breathless','muscle_aches','nausea','fatigue','confusion',
                   'diarrhoea','chest_pain','headache','sore_throat','rhinitis',
                   'rash','conjunctivitis','anosmia','hoarse_voice','appetite_loss',
                   'abdominal_pain','wheeze']
    
    # Initialise a dictionary of Symptom Diaries to chase up
    chase_up = {'ATACCC':list(),
                'INSTINCT':list()}
    
    # Create a list of participants with entered diaries
    entered_diaries = list(diary_dict.keys())
    
    # Loop though IDs from Symphony
    for i in symphony_ids:
        print(i)
        # If their diary is not present in the TRACKER DATABASE
        if i not in entered_diaries:
            
            # Add it to either ATACCC or INSTINCT chase_up list
            if i[0:3] == 'ATA':
                chase_up['ATACCC'].append(i)
            elif i[0:3] == 'INS':
                chase_up['INSTINCT'].append(i)
            else:
                print('help')
            
            # Create an empty list for them
            empty = list()
            for n in range(1131):
                empty.append('')
            
            # Add them, alogn with their empty list, to the final dictionary
            final_dict[i] = empty
        
        # if their Symptom Diary is present
        else:
            
            # Import the data from the Symptom Diary
            filename = diary_dict[i]
            diary_dataframe = getData(filename)
            
            # Organise into a useful dictionary format
            symptom_dict = reorgData(diary_dataframe)
            
            # Loop though ORDERED column list
            participant_data = list()
            for col in column_list:
                
                # Loop through each score of the symptoms
                for s in symptom_dict[col]:
                    
                    # Add it to a continous list
                    participant_data.append(s)
            
            # Add it to the final dictionary
            final_dict[i] = participant_data
            
    return(final_dict, chase_up)
    
final_dict, chase_up = collateData()

####    Step 8    ####    Export final data to as '.csv'    ####

def getArray(dictionary):
    
    # Turn dictionary entries to an array
    data = list(dictionary.values())
    an_array = np.array(data)
    
    return(an_array)

savetxt('/Outputs/raw_scores_output.csv', getArray(final_dict), delimiter=',',fmt='%s')
end = time.time()

print('Time ellapsed: ' + str((end-start)))

del start
del end
#del col_array
#del data