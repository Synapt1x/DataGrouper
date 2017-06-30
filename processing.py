"""
Data Grouper Processing Functions
============================
Created by: Chris Cadonic
For: Utility in Dr. Mandana Modirrousta's Lab
----------------------------
This file contains code necessary for processing excel files in the
grouper.py program. Functions here process files, the input of the 
user, and also call utils and custom_gui functions to invoke
either optional functionality or request information from the user.

============================


"""
import sys
import pandas as pd
import utils
from tkinter import messagebox, filedialog


def get_directory(root, initial_dir, title_dir):
    """ Ask the user for the appropriate directory """
    try:
        get_dirname = filedialog.askdirectory(
            parent=root, initialdir=initial_dir,
            title=title_dir)
        if not get_dirname:
            raise ValueError("empty string")
        return get_dirname
    except ValueError:
        messagebox.showinfo("Invalid directory - Failed", "Operation has "
                                                          "been cancelled...")
        exit()


def process_file(file_name, cols, get_block=False):
    """ Parse an excel file and return a dataframe trimmed based on which 
    columns are required for the given task """

    # setup the excel file
    excel = pd.ExcelFile(file_name)

    # now read excel file data into a DataFrame
    datafile = pd.read_excel(excel)

    # split name in the case of the face learning task
    if get_block:
        text_split = file_name.split(sep='-')
        block_num = text_split[2].split(sep='_')[0][-1]

        # add column for block num
        datafile['Block'] = block_num
        datafile['Block'] = datafile['Block'].astype(int)

    return datafile[cols]


def determine_task(root, dirname, prefix):
    """ Determine which task will be amalgamated by grouper.py """
    # initialize
    data_dirpath = ''
    cols = []
    sort_cols = []
    get_block = False

    if len(sys.argv) > 1:
        task = str(sys.argv[1])
    else:
        # Ask user to identify the data directory
        data_dirpath = get_directory(root, dirname, 'Please select the data '
                                                    'directory.')
        task = data_dirpath.split('/')[-1]

    # identify the columns required for each task
    if task == 'ActionValue':
        messagebox.showinfo('Default found for task',
                            'Default settings loaded for this task.')
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-ReversalLearning' \
                '/ReversalLearning-ExcelFiles/ActionValue/'
        get_block = False

        cols = ['Subject', 'Session', 'WinningAction[Trial]', 'Proba',
                'WinLose', 'ActionMade', 'Condition', 'Accuracy',
                'RestCount', 'Score[Trial]']

        sort_cols = ['Subject', 'Session']

    elif task == 'Prob_RL':
        messagebox.showinfo('Default found for task',
                            'Default settings loaded for this task.')
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-ReversalLearning' \
                '/ReversalLearning-ExcelFiles/Prob_RL/'
        get_block = False

        cols = ['Subject', 'Session', 'WinningColor[Trial]', 'Proba',
                'WinLose', 'ColorPicked', 'Condition', 'Accuracy',
                'RestCount', 'Score[Trial]']

        sort_cols = ['Subject', 'Session']

    elif task == 'FaceLearning-Learning':
        messagebox.showinfo('Default found for task',
                            'Default settings loaded for this task.')
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-FaceLearning/FaceLearning-Learning/'
        get_block = True

        cols = ['Subject', 'Block', 'Trial', 'TextDisplay6.RESP']

        sort_cols = ['Subject', 'Block', 'Trial']

    elif task == 'FaceLearning-Recall':
        messagebox.showinfo('Default found for task',
                            'Default settings loaded for this task.')
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-FaceLearning/FaceLearning-Recall/'
        get_block = True

        cols = ['Subject', 'Block', 'Trial', 'CorrectAnswer',
                'TextDisplay35.RESP', 'TextDisplay36.RESP']

        sort_cols = ['Subject', 'Block', 'Trial']
    elif task == 'FaceLearning':
        messagebox.Message('Default found for task; default settings loaded')
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-FaceLearning/Output/'
        get_block = False

    return data_dirpath, cols, sort_cols, task, get_block


def process_dataframe(df, task, sort_cols, output_dirname):
    """ Process the data frame for additional calculated columns """

    # initialize and leave empty if not reversal task
    reversals_df = pd.DataFrame({})
    winshifts_df = pd.DataFrame({})
    avg_winshifts_df = pd.DataFrame({})

    # sort by the required identifying variables if specified
    if sort_cols:
        df.sort_values(sort_cols, inplace=True)

    # assign groups based on subject number
    df['Group'] = df.apply(utils.assign_group, task=task, axis=1)

    if task == 'ActionValue' or task == 'Prob_RL':
        ''' all data for reversal task '''
        # first remove practice sessions and group by subject and session
        df = df.loc[df['Condition'] != 'Practice']  # remove defined practice
        df = df.loc[~df['Condition'].isnull()]  # remove empty conditions

        # add additional features for analysis
        df['Error Switch'] = utils.determine_error_switches(df, task)

        # add a col for determining the number of reversals for each subject
        utils.determine_max_reversals(df, task)

        ''' reversals sheet '''
        reversals_df = utils.determine_max_reversals(df, task)

        ''' winshifts sheets '''
        winshifts_df, avg_winshifts_df = \
            utils.determine_winshift_proportions(df)

    elif task == 'FaceLearning-Recall':
        ''' process all data for face learning task '''

        # firstly determine true confidence values for recall
        df['Recall Confidence'] = utils.determine_confidence(df)

        # determine whether the subject had correctly recalled or recognized
        #  the face
        df = utils.determine_face_accuracy(df)

        # scale confidence measures into proportions
        df['Recall Confidence'] = df['Recall Confidence'] / 5
        df['Recog Confidence'] = df['Recog Confidence'] / 5

    elif task == 'FaceLearning-Learning':
        ''' process all data for face learning acquisition task '''

        # firstly rename the columns as appropriate
        df.rename(columns={'TextDisplay6.RESP': 'Learning Confidence'},
                  inplace=True)

        # scale learning confidence into proportion
        df['Learning Confidence'] = df['Learning Confidence'] / 5

    return df, reversals_df, winshifts_df, avg_winshifts_df


if __name__ == '__main__':
    pass
