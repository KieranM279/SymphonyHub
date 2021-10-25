# Symphony Creation and Updates


## Symptom diary import

#### Pre-requisite files
* **symptom_names.txt** - A text document containing a list of the symptoms that are investigated by the study and their respective column names within the individual participant symptom diaries

* **mac_dir.txt** - A tab-separated text file of all the directory locations required by the script. This has to be updated and changed for the needs of the user and with the addition of new cohorts

#### Requirements
```python
import os
import pandas as pd
import numpy as np
from numpy import savetxt
import time
```

#### Usage
```python
# Import the list of Symptom names from a text file
symptoms = list(getNames('symptom_names.txt').values())
# Import a single Symptom Diary using its filename
diary_dataframe = getData('filename.xlsx')
# Reorganise dataframe into a dictionary
symptom_dict = reorgData(diary_dataframe)
```
#### Methods
###### Step 1 - Import the list of Symptom names
This function in used to import the names for each symptom as they should appear in Symphony. It parses a text file which contains the names and outputs is as a dictionary. I only keep a list of values from the dictionary, rather than the whole dictionary. I am yet to change this.
```python
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
```
###### Step 2 - Function to import a single Symptom Diary
This reads the Input filename and then decides the directory to use based on the first three letter. It can then import the data as a dataframe, selecting the first 31 rows (minus the ID and dates row). The text data is then replaced with their numerical equivalents, and NA values are removed. The last section is there to remove zeroes from the scores section when there are not any symptoms entered. Its not the cleanest but it works.
```python
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

    ###  Remove erroneous zeroes in the scores section ###

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
```
###### Step 3 - Reorganise the dataframe data into a usable dictionary format
This function takes in a dataframe containing a single symptom diary of data and outputs a dictionary of lists where the keys are the individual symptoms of the participant. Each list is ordered by day and missing days are imputed as blanks to match full length of the study window (Days -10 to 27).
```python
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
```
###### Step 4 -


## Temperature import script

#### Pre-requisite filenames
* **day_names.txt** - A text file containing a list of all the day names that the participant may have recorded their temperature (Day 0 - 27).

#### Usage
```python
# Import the list of participants from Symphony
symphony_ids = getSymphony()
# Import the list of Days from a text file
days = getDays(days_filename)
# Create a dictionary of partipants and the filenames of their Symptom Diary
diary_dict = DiaryDictmaker()
# Create a dictionary of the Temperature data from the Symptom Diaries
temperature_data = collateData()
```
#### Method

###### Step 1 - Import a list of the participant IDs
First step is to import the list of IDs from Symphony and save them as a list. This makes sure I output the final dataset in the right format.
```python
def getSymphony():

    path = str(symphony_path + symphony_filename)

    # Import list of IDs from the Symphony MRS
    fields = ['id_sub']
    participants = pd.read_excel(path,
                                 sheet_name='Raw Temperatures',
                                 usecols=(fields))
    participants = participants.dropna()
    part_list = list()

    # Create a list of the IDs
    for p in participants['id_sub']:

        part_list.append(p)

    return(part_list)
```

###### Step 2 - Create a list of Study days for the columns
```python
def getDays(filename):

    # Open the file with the name conversions
    names = open(filename)
    day_list = list()

    # Loop through the line of the symptom names file
    for ln in names.readlines():

        ln = ln.strip()

        # Create a list of the days
        day_list.append(ln)

    return(day_list)
```

###### Step 3 - Get a dictionary of all the Symptom Diary Filenames
This step is used to create a dictionary of all the filenames in the ATACCC and INSTINCT cohort. The participant IDs are used as the keys for the dictionary.

NOTE: Currently has no way to deal with the ATACCC 'b' participants.
```python
def DiaryDictmaker():
    dictionary = {}

    # Get a list of filenames from the TRACKER DATABASE
    ataccc_diary_list = os.listdir(ataccc_symptom_diaries)
    instinct_diary_list = os.listdir(instinct_symptom_diaries)

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

    # Loop through the list of filenames
    for filenameATA in ataccc_diary_list:

        # Skip if it is not a Symptom Diary
        if filenameATA[0:3] != 'ATA':
            continue

        # Create a dictionary of the participants and their diary filename
        dictionary[str(filenameATA[0:7])] = filenameATA

        if str(filenameATA[7]) == 'i':
            dictionary[str(filenameATA[0:8])] = filenameATA

    return(dictionary)
```
