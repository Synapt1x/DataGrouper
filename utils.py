"""
Data Grouper Utils
============================
Created by: Chris Cadonic
For: Utility in Dr. Mandana Modirrousta's Lab
----------------------------
This file contains code for additional tools for parsing, calculating, 
and creating new columns for data analysis during grouping operations.
There are plans to continue with expanding the list of available
utilities, but the current utilities available include:

============================
determine_choice_made: determine which side was selected in the task

determine_error_switches: determine whether the patient made an erroneous 
switch by changing sides after choosing a winning option

"""


def determine_choice_made(df):
    '''Add a column for choices if the task is action value'''
    x_mid = 320

    choice_made = [1 if x_val < x_mid else 2 for x_val in df['XPosition']]

    return choice_made


def determine_error_switches(df, task):
    ''' Add a column showing whether erroneous reversals are made'''
    if (task == 'ActionValue'):
        choice_made = determine_choice_made(df)
    else:
        choice_made = list(df['ColorPicked'])

    conditions = list(df['Condition'])
    wins = list(df['WinLose'])
    indices = list(df.index.values)
    error_switch = [1 if ((wins[cur - 1] == 'win')
                        and (choice_made[cur] != choice_made[cur - 1])
                        and (not (indices[cur] == 6 and indices[cur - 1] > 6))
                        and (indices[cur] != 0)
                        and (isinstance(conditions[cur - 1], str)))
                        else 0 for cur in range(1, len(wins))]
    error_switch.insert(0, 0) # cannot be a switch at the very beginning

    return error_switch

def assign_group(subject_row):
    """ Define which group this subject belongs to """
    # add an additional column for separating out groups
    controls = {401, 402, 403, 404, 405, 418}
    shams = {758, 762, 763, 764}
    treat = {754, 756, 757, 759, 760, 761, 766, 767}
    if subject_row['Subject'] in controls:
        return 'control'
    elif subject_row['Subject'] in shams:
        return 'sham'
    elif subject_row['Subject'] in treat:
        return 'treatment'
    else:
        return 'NA'


def main():
    pass

if __name__ == '__main__':
    main()