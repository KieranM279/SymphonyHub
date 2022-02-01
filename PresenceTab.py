#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:55:29 2022

@author: kieran
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 14:50:25 2022

@author: kieran
"""

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

###### Helper functions ######

def MotifF(motif, string):

    # Sets the length of the motif and string
    motif_length = len(motif)
    string_length = len(string)
    
    if motif_length > string_length:
        Bool = False
        return(Bool)

    # Loops as a sliding window through the String
    for i in range(string_length):

        # Potential match to motif
        P_match = string[i:i+motif_length]

        # Conditional identifying the presence of the motif
        if len(P_match) < motif_length:
            break
        elif motif == P_match:
            Bool = True
            #print(i)
            #print(len(P_match))
            break
        else:
            Bool = False

    return(Bool)


def idTrans(ids, n):
    
    
    # Set to Booleans to account for retrospectively recruited indexes
    retro_indexA = False
    retro_indexB = False
    
    if ids[-1] == 'A':
        retro_indexA = True
        ids = ids[0:len(ids)-1]
    
    if ids[-1] == 'B':
        retro_indexB = True
        ids = ids[0:len(ids)-1]
    
    
    # List the five cohorts
    cohorts = ['ATA','INS','FUZR','FUZHH','BUZ']
    
    dictionary = {'cohort':'',
                  'participant':''}
    
    # Loop through all the possible cohorts
    for c in cohorts:
        
        # if the cohort motif is present in the ID
        if MotifF(c,ids):
            
            
            # Remove the ID and transform remainder to an integer
            ids = ids.replace(c,'')
            
            # Save participant info
            dictionary['cohort'] = c
            dictionary['participant'] = int(ids)
    
    
    
    # Define the number of digits in the participant number
    if (dictionary['participant'] <= 9):
        length = 1
    
    elif (dictionary['participant'] >=10 and dictionary['participant'] <= 99):
        length = 2
    
    elif (dictionary['participant'] >= 100 and dictionary['participant'] <= 999):
        length = 3
        
    else:
        print('help: The participant number exceeds 999')
    
    # Identify the nunber of zeros needed
    zeros = n-length
    
    n_zero = ''
    
    for z in range(zeros):
        
        n_zero = n_zero + '0'
    
    
    if retro_indexA:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']) + 'A')
    elif retro_indexB:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']) + 'B')
    else:
        return(dictionary['cohort'] + n_zero + str(dictionary['participant']))


#### Get a list of participants from Symphony ####

def getSymphony(filename):
    
    
    path = str(dir_dict['MRS_path'] + symphony_filename)
    
    # Import the relevent data from the Symphony spreadsheet
    fields = ['id_sub']
    data = pd.read_excel(path,
                         sheet_name='Individual Symptoms',
                         usecols=(fields))
    
    id_list = list()
    
    # Loop through data and append IDs to a list
    for i in data['id_sub']:
        id_list.append(i)

    return(id_list)

participant_ids = getSymphony(symphony_filename)


####    Step 2    ####  Create a dictionary of participant SD filenames  ####

def DiaryDictmaker():
    dictionary = {}
    
   # Get a list of filenames from the TRACKER DATABASE
    ataccc_diary_list = os.listdir(dir_dict['ataccc_symptom_diaries'])
    instinct_diary_list = os.listdir(dir_dict['instinct_symptom_diaries'])
    bolton_diary_list = os.listdir(dir_dict['bolton_symptom_diaries'])
    london_diary_list = os.listdir(dir_dict['london_symptom_diaries'])
    fusion_diary_list = os.listdir(dir_dict['fusion_symptom_diaries'])
    
    ####    INSTINCT Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameINS in instinct_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameINS[0:3] != 'INS':
            continue
        
        elif str(filenameINS[7]) == 'i':
            dictionary[str(filenameINS[0:8])] = filenameINS
            continue
        
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameINS[0:7])] = filenameINS
        
    
    ####    ATACCC Diary Filenames    ####
    
    # Loop throught the list of filenames
    for filenameATA in ataccc_diary_list:
        
        # Skip if it is not a Symptom Diary
        if filenameATA[0:3] != 'ATA':
            continue
        
        elif str(filenameATA[7]) == 'i':
            dictionary[str(filenameATA[0:8])] = filenameATA
            continue
        
        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameATA[0:7])] = filenameATA
      
    
    ####    FUSION Diary Filenames    ####
    
    # Loop through list of filenames
    for filenameFUSHH in fusion_diary_list:
        
        # Skip of not a Symptom Diary
        if filenameFUSHH[0:4] != 'FUZH':
            continue
        
        # Add to dictionary
        dictionary[idTrans(str(filenameFUSHH[0:9]),3)] = filenameFUSHH
    
    
    ####    ATACCC2 Bolton Diary Filenames    ####
    
    # Loop through th list of filenames
    for filenameBUZ in bolton_diary_list:
        
        # Skip if not a Symptom Diary
        if filenameBUZ[0:3] != 'BUZ':
            continue
        
        # Account for Non-recruited indexes
        elif (str(filenameBUZ[7]) == 'A' or str(filenameBUZ[7]) == 'B'):
            dictionary[idTrans(str(filenameBUZ[0:8]),3)] = filenameBUZ
            continue
            
        # Add to dictionary
        dictionary[idTrans(str(filenameBUZ[0:7]),3)] = filenameBUZ
    
    
    ####    ATACCC2 London Diary Filenames    ####
    
    # Loop through list of filenames
    for filenameFUZR in london_diary_list:
        
        # Skip if not a filename
        if filenameFUZR[0:4] != 'FUZR':
            continue
        
        # Account for non-recriuted indexes
        elif (str(filenameFUZR[8]) == 'A' or str(filenameFUZR[8]) == 'B'):
            dictionary[idTrans(str(filenameFUZR[0:9]),3)] = filenameFUZR
            continue
        
        # Add to dictionary
        dictionary[idTrans(str(filenameFUZR[0:8]),3)] = filenameFUZR
        
    
    return(dictionary)

diary_dict = DiaryDictmaker()

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


####### Import all thw presence data for individual symptoms #######
# This data is generated by the script 'SymptomPresenceImport.py'

def getPresence():
    
    # Isolate the path to the presence data
    path = dir_dict['output_dir'] + 'presence_output.csv'
    
    # Import all the data in that '.csv'
    data = pd.read_csv(path,
                       index_col=(0))
    
    # Drop the columns thats I don't want to use
    data = data.drop(['normal','lower','upper','gi','symp','system','cffd2g1','sburden'],
                     axis=1)
    
    symptoms = list(data.columns)
    
    data = data.to_dict(orient='index')
    
    return(data, symptoms)

presence_data, symptoms_oi = getPresence()


####    Step 5    ####    Function to import entire symptom diaries    ####

def getData(filename):
    
    if filename[0:3] == 'INS':
        ###   INSTINCT   ###
        path = str(dir_dict['instinct_symptom_diaries'] + str(filename))
        
    elif filename[0:3] == 'ATA':
        ###   ATACCC   ###
        path = str(dir_dict['ataccc_symptom_diaries'] + str(filename))
        
    elif filename[0:3] == 'BUZ':
        ###   ATACCC2 Bolton   ###
        path = str(dir_dict['bolton_symptom_diaries'] + str(filename))
        
    elif filename[0:4] == 'FUZR':
        ###   ATACCC2 London   ###
        path = str(dir_dict['london_symptom_diaries'] + str(filename))
    
    elif filename[0:4] == 'FUZH':
        ###   FUSION   ###
        path = str(dir_dict['fusion_symptom_diaries'] + str(filename))
    
    
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
    data2 = data2.replace('N', '')
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
        
    
    data2 = data2[2:23]
    return(data2)

####    Step 6    #### Re-organises dataframe into a dictionary format ####

def reorgData(df, symptom_list):
    
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
    for s in symptoms_oi:
        
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



def getAlphas(part_diary_dict):
    
    dictionary = {}
    
    # Define the new list of days that are to be used within Symphony
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    
    # Loop through the symptoms of interest
    for i in symptoms_oi:
        
        
        # Loop through the days from Symphony (DU, Day -10: Day 27)
        for di, d in enumerate(new_days):
            
            # If the symptom is not present on that day, move on to the next
            if part_diary_dict[i][di] == '':
                continue
            
            # If the symptoms is present regardless of severity
            elif part_diary_dict[i][di] != '':
                
                # Mark the days as the onset of the symptom
                start = d
                dictionary[i] = start.strip('DAY *')
                break
    
    # Loop through the symptoms of interest again
    for b in symptoms_oi:
        
        # If it hasn't been adressed by the previous loop
        if b not in dictionary.keys():
            
            # Assign the symptoms as never felt
            dictionary[b] = 'never'
            
    return(dictionary)



def getOmegas(part_diary_dict):
    
    dictionary = {}
    
    # Define the new list of days that are to be used within Symphony
    new_days = ['DU','DAY -10*', 'DAY -9*', 'DAY -8*', 'DAY -7*', 'DAY -6*', 
                'DAY -5*', 'DAY -4*', 'DAY -3*', 'DAY -2*', 'DAY -1*',
                'DAY 0', 'DAY 1', 'DAY 2', 'DAY 3', 'DAY 4', 'DAY 5', 'DAY 6',
                'DAY 7', 'DAY 8', 'DAY 9', 'DAY 10', 'DAY 11', 'DAY 12',
                'DAY 13', 'DAY 14', 'DAY 15', 'DAY 16', 'DAY 17', 'DAY 18',
                'DAY 19', 'DAY 20', 'DAY 21', 'DAY 22', 'DAY 23', 'DAY 24', 
                'DAY 25', 'DAY 26', 'DAY 27']
    
    # Loop through the symptoms of interest
    for i in symptoms_oi:
        
        # Loop through the days, in reverse, from Symphony (Day 27:Day -10, DU)
        for di, d in enumerate(reversed(new_days)):
            
            # If the symptom in not present on that day, move onto the next
            if part_diary_dict[i][-di-1] == '':
                continue
            
            # If the symptoms is present regardless of severity
            elif part_diary_dict[i][-di-1] != '':
                
                # Mark the days as the end of the symptom
                start = d
                dictionary[i] = start.strip('DAY *')
                break
    
    # Loop through the symptoms of interest again
    for b in symptoms_oi:
        
        # If it hasn't been adressed by the previous loop
        if b not in dictionary.keys():
            
            # Assign the symptoms as never felt
            dictionary[b] = 'never'
            
    return(dictionary)



def collateData():
    
    dictionary = {}
    
    columns = list()
    
    # Loop through the list of symptoms
    for symp in symptoms_oi:
        
        # Create the column names for each symptoms
        columns.append(symp)
        columns.append(symp + '_onset')
        columns.append(symp + '_end')
    
    # Loop through the list of participants within symphony
    for i in participant_ids:
        
        print(i)
        entry = {}
        
        # If the participant doesn't have a symptoms diary
        if i not in diary_dict.keys():
            
            # Mark every field with No Diary ('ND')
            for s in columns:
                entry[s] = 'ND'
            dictionary[i] = entry
        
        else:
            
            # Import and transform the participant's symptoms diaries
            data = getData(diary_dict[i])
            data = reorgData(data, symptoms)
            
            # Create a dictionary of the onset and end of each symptom
            alphaDict = getAlphas(data)
            omegaDict = getOmegas(data)
            
            
            # Loop through all the symptoms of interest
            for symptom in symptoms_oi:
                
                # Assing the presence of the symptoms as found in another script
                entry[symptom] = presence_data[i][symptom]
                
                # If the symptom is not addressed by participant
                if presence_data[i][symptom] == '.':
                    
                    entry[symptom + '_onset'] = '.'
                    entry[symptom + '_end'] = '.'
                
                # If the participant has No Diary
                elif presence_data[i][symptom] == 'ND':
                    
                    entry[symptom + '_onset'] = 'ND'
                    entry[symptom + '_end'] = 'ND'
                
                # If the symptoms is present or not
                elif (presence_data[i][symptom] == 'Y' or
                      presence_data[i][symptom] == 'N'):
                    
                    # Assign the symptoms onset and end
                    entry[symptom + '_onset'] = alphaDict[symptom]
                    entry[symptom + '_end'] = omegaDict[symptom]
            
            dictionary[i] = entry
    
    return(dictionary)
    
final_dict = collateData()


####    Step 6    ####    export to csv   ####

def getArray(dictionary):
    
    data = pd.DataFrame.from_dict(dictionary)
    data = data.replace('U','DU')
    
    return(data.transpose())

data = getArray(final_dict)

data.to_csv(dir_dict['output_dir'] + 'tab_presence_output.csv')

end = time.time()
print('Total time ellapsed: ' + str(end-start))
del start
del end