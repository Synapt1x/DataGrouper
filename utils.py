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
import numpy as np


def determine_error_switches(df, task):
    """ Add a column showing whether erroneous reversals are made """

    if (task == 'ActionValue'):
        choice_made = list(df['ActionMade'])
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

    controls = {401, 402, 403, 404, 405, 418}
    shams = {758, 762, 763, 764}
    treat = {754, 756, 757, 759, 760, 761, 766, 767}

    # check for set membership to determine where subject belongs
    if subject_row['Subject'] in controls:
        return 'control'
    elif subject_row['Subject'] in shams:
        return 'sham'
    elif subject_row['Subject'] in treat:
        return 'treatment'
    else:
        return 'NA'

def determine_max_reversals(df, project):
    """ Add a column that denotes the maximum number of reversals for a 
    subject """

    # first assign the max rest count
    if project == 'ActionValue':
        max_trials = 100
    else:
        max_trials = 70

    # extract condition information
    df['Reversal'] = list(df['Condition'].str.extract('(\d+)',
                                          expand=False).fillna(0).astype(int))

    # fix any erroneously added ?'s in RestCount column
    df['RestCount'] = np.where(df['Condition'] == 'IL', max_trials,
                                df['RestCount'])

    # remove additional reversals after task has been completed
    df['Reversal'] = np.where(df['RestCount'].fillna(0).astype(int) < 0, 0,
                              df['Reversal'])

    # determine max number for each subject grouped by trial
    df['Num Reversals'] = df.groupby(['Subject', 'Session'])[
        'Reversal'].transform('max')


def determine_confidence(df):
    """ Determine the true confidence value based on whether or not the 
    subject actually answered or not """

    # firstly rename textdisplay columns with proper confidence labels
    df.rename(columns={'TextDisplay35.RESP': 'Recall Confidence',
                       'TextDisplay36.RESP': 'Recog Confidence'}, inplace=True)

    df['Recall Choice'] = df['Recall Choice'].astype(str)

    # set any confidence levels to 0 if they did not actually answer
    correct_confidence = np.where(df['Recall Choice'] != 'nan', df['Recall '
                                                           'Confidence'], 0)

    return correct_confidence

def determine_face_accuracy(df):
    """ Determine whether the subject was correct or not in either recalling 
    or recognizing the face """

    # check if recall matches any the correct answer column
    recall_acc = np.where(df['Recall Choice'] == df['CorrectAnswer'], 1, 0)
    recog_acc = np.where(df['Recog Choice'] == df['CorrectAnswer'], 1, 0)

    return recall_acc, recog_acc


def main():
    pass

if __name__ == '__main__':
    main()