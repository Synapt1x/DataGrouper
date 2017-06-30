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
import pandas as pd
from itertools import permutations
from tkinter import messagebox


def gkgamma(m, n):
    """
    From sample calculations of the goodman kruskal gamma calculation, 
    this function determines the gamma correlation between two ordinal 
    variables.

    :param m: a list of values for variable 1
    :param n: a list of values for variable 2
    :return: return the gamma correlation between variable 1 and variable 2
    """
    nc = 0  # number of concordant pairs or noninversions
    nd = 0  # number of discordant pairs or inversions
    nt = 0  # number of ties

    # complete calculation for pairs (i, j)
    for (i, j) in permutations(range(len(m)), 2):
        # determine number of inversiona and noninversions
        diff_m = m[i] - m[j]
        diff_n = n[i] - n[j]

        product = diff_m * diff_n

        if product > 0: # noninversion
            nc += 1
        elif product < 0: # inversion
            nd += 1
        else: # tie
            nt += 1
    return (nc - nd)/(nc + nd + nt)


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

def assign_group(subject_row, task):
    """ Define which group this subject belongs to """

    controls = {401, 402, 403, 404, 405, 418}
    shams = {758, 762, 763, 764, 768}
    treat = {754, 756, 757, 759, 760, 761, 766, 767}

    # check for set membership to determine where subject belongs
    if subject_row['Subject'] in controls:
        return 'control'
    elif subject_row['Subject'] in shams:
        return 'sham'
    elif subject_row['Subject'] in treat:
        if task == 'FaceLearning' or task == 'FaceLearning-Recall' or task \
                == 'FaceLearning-Learning':
            if subject_row['Block'] < 5:
                return 'pre-treatment'
            else:
                return 'post-treatment'
        else:
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

    # extract data frame for just reversals
    reversals_df = df[['Subject', 'Session', 'Group',
                       'Num Reversals']].copy()

    # collapse over subject and session
    reversals_df.drop_duplicates(inplace=True)
    reversals_df.sort_values('Group', inplace=True)

    return reversals_df

def determine_winshift_proportions(df):
    """ Add a column that denotes the proportion of winshifts conducted
    by a subject in a block """

    ''' winshifts all data '''
    # first get the total amount of winshift errors in each session
    grouper = df.groupby(['Subject', 'Session'])
    df['winshifts'] = grouper['Error Switch'].transform('sum')

    # create two columns for use in calculating total win follow-ups
    df['shifted winlose'] = df['WinLose'].shift(1)
    df['win followup'] = np.where(df['shifted winlose'] == 'win', 1, 0)

    df['num followups'] = df.groupby(['Subject', 'Session'])['win ' \
                                                 'followup'].transform('sum')

    # simply output all the data for only winshifts
    winshifts = df[['Subject', 'Session', 'Group', 'winshifts',
                    'num followups']].copy()

    # calculate winshift proportions for each session
    winshifts['Winshift Proportions'] = winshifts['winshifts']/winshifts[
        'num followups']

    # collapse over subject and session
    winshifts.drop_duplicates(inplace=True)
    winshifts.sort_values('Group', inplace=True)

    ''' winshift averages '''
    # determine how many trials followed win feedback for each session
    grouper = df.groupby(['Group', 'Session'])
    winshift_errors = grouper['Error Switch'].sum().to_frame('winshifts')
    winshift_all = grouper['win followup'].sum().to_frame('num followups')

    # combine the two Series' into a new output frame for winshifts
    winshifts_avg = pd.concat([winshift_errors, winshift_all], 1)

    winshifts_avg['Mean Proportion'] = winshifts_avg['winshifts']/\
                                   winshifts_avg['num followups']

    # remove temporary columns
    df.drop(['shifted winlose', 'win followup'], 1, inplace=True)

    return winshifts, winshifts_avg


def determine_confidence(df):
    """ Determine the true confidence value based on whether or not the 
    subject actually answered or not """

    # firstly rename textdisplay columns with proper confidence labels
    df.rename(columns={'TextDisplay35.RESP': 'Recall Confidence',
                       'TextDisplay36.RESP': 'Recog Confidence'}, inplace=True)

    df['Recall Choice'] = df['Recall Choice'].astype(str)

    # set any confidence levels to 0 if they did not actually answer
    correct_confidence = np.where(df['Recall Choice'] != 'nan', df['Recall '
                                                        'Confidence'], 'nan')

    return correct_confidence.astype(float)


def determine_face_accuracy(df):
    """ Determine whether the subject was correct or not in either recalling 
    or recognizing the face """

    # check if recall matches any the correct answer column
    recall_acc = np.where(df['Recall Choice'] == df['CorrectAnswer'], 1, 0)
    recog_acc = np.where(df['Recog Choice'] == df['CorrectAnswer'], 1, 0)

    df['Recall Acc'], df['Recog Acc'] = recall_acc, recog_acc
    df['Recall Acc'] = np.where(df['Recall Choice'] != 'nan',
                                df['Recall Acc'], 'nan')
    df['Recall Acc'] = df['Recall Acc'].astype(float)

    return df


def merge_facelearning(data_dirname):
    """ Merge the face learning excels at the time of running the program """
    #initialization
    datafiles = []

    files = ['FaceLearning-Recall-Output.xlsx',
             'FaceLearning-Learning-Output.xlsx']

    for file_name in files:
        try:
            # setup the excel file
            excel = pd.ExcelFile(file_name)

            # now read excel file data into a DataFrame
            datafile = pd.read_excel(excel)

            datafiles.append(datafile)
        except:
            messagebox.showwarning("Error in loading excel; check to make "
                                "sure the other face learning excel files " 
                                "have been output already.")
            return

    return pd.merge(datafiles[0], datafiles[1])

def calculate_facelearning_measures(all_data_df):
    """ Calculate mean performance statistics and JOL, RCJ and FOK measures
    for the face learning task """

    # initialize variables
    rcj = []
    fok = []
    block_indices = []

    # firstly, make a copy of the data frame
    df = all_data_df.copy()

    grouper = df.groupby(['Subject', 'Block'])

    # first get the total amount of correct answers in each block
    df['Recall Count'] = np.where(df['Recall Acc'].isnull(), 0, 1)
    df['Recall Count'] = grouper['Recall Count'].transform('sum')
    df['Recall Corr'] = grouper['Recall Acc'].transform('sum')/df['Recall ' \
                                                                  'Count']
    df['Recog Corr'] = grouper['Recog Acc'].transform('sum')/6

    # next run the gamma calc. and JOL calc. for each block
    df['JOL'] = df['Recall Corr'] - grouper['Learning ' \
                                            'Confidence'].transform('sum')/6

    # calculate gamma measures for RCJ and FOK
    for group in grouper:
        # extract confidence judgments
        recall_conf = list(group[1]['Recall Confidence'].values)
        recog_conf = list(group[1]['Recog Confidence'].values)

        # extract memory performance
        recall_acc = list(group[1]['Recall Acc'].values)
        recog_acc = list(group[1]['Recog Acc'].values)

        # record which subject/group combination had each gamma
        block_indices.append(group[0])

        # calculate gamma measures and store these into lists
        rcj.append(gkgamma(recall_conf, recall_acc))
        fok.append(gkgamma(recog_conf, recog_acc))

    # amalgamate the necessary results into one df grouped by block
    summary_df = df[['Subject', 'Block', 'Group', 'Recall '
                            'Corr', 'Recog Corr', 'JOL']].drop_duplicates()
    summary_df['RCJ'] = rcj
    summary_df['FOK'] = fok
    summary_df.sort_values(['Group', 'Subject', 'Block'], inplace=True)

    # aggregate plot_df for summarizing means
    plot_grouper = summary_df.groupby(['Group'])
    new_df = plot_grouper[['Recall Corr', 'Recog Corr', 'JOL',
                           'RCJ', 'FOK']].transform('mean')
    new_df['Group'] = summary_df['Group']

    cols = ['Group', 'Recall Corr', 'Recog Corr', 'JOL', 'RCJ', 'FOK']

    plot_df = new_df[cols].drop_duplicates()

    return summary_df, plot_df


if __name__ == '__main__':
    pass
