"""
Data Grouper
============================
Created by: Chris Cadonic
For: Utility in Dr. Mandana Modirrousta's Lab
----------------------------
This program was developed to facilitate data organization
by grouping data from previous experiments into a single
output excel file.

This program builds upon previous work done by myself in
Dr. Debbie Kelly's lab, and by work done by Dr. Modirrousta's
son.

There are also additional tools for parsing, calculating, and
creating new columns for data analysis during grouping operations.
There are plans to continue with expanding the list of available
utilities, but the current utilities available include:

== mean

"""
import sys
from os import chdir, path, sep

import pandas as pd
import utils
from tkinter import Tk, filedialog, messagebox
from custom_gui import ask_columns
import glob, time
import platform


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
        messagebox.showinfo("Invalid directory - Failed", "Operation "
                                  "has been cancelled...")
        exit()


def process_example(df):
    """ Process the first data frame in the data directory to determine
    what will be needed from this data. """
    cols = ask_columns(list(df.columns.values))


def process_file(file_name, cols, get_block = False):
    """ Parse an excel file and return a dataframe trimmed based on which 
    columns are required for the given task """

    # setup the excel file
    excel = pd.ExcelFile(file_name)

    # now read excel file data into a DataFrame
    datafile = pd.read_excel(excel)

    # if columns have not been specified yet, call process example to get info
    sort_cols = process_example(datafile)

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
        task = data_dirpath.split(sep)[-1]

    # identify the columns required for each task
    if task == 'ActionValue':
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
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-FaceLearning/FaceLearning-Learning/'
        get_block = True

        cols = ['Subject', 'Block', 'Trial', 'TextDisplay6.RESP']

        sort_cols = ['Subject', 'Block', 'Trial']

    elif task == 'FaceLearning-Recall':
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-FaceLearning/FaceLearning-Recall/'
        get_block = True

        cols = ['Subject', 'Block', 'Trial', 'CorrectAnswer',
                'TextDisplay35.RESP', 'TextDisplay36.RESP']

        sort_cols = ['Subject', 'Block', 'Trial']
    elif task == 'FaceLearning':
        if not data_dirpath:
            data_dirpath = prefix + \
                'MandanaResearch/OCD-Facelearning/Output/'
        get_block = False

    # print which columns will be pulled into the output excel
    print("Current columns to be captured from the excel files:\n")
    for col in cols: print(col)

    return data_dirpath, cols, sort_cols, task, get_block


def process_dataframe(df, task, sort_cols, output_dirname):
    """ Process the data frame for additional calculated columns """

    # initialize and leave empty if not reversal task
    reversals_df = pd.DataFrame({})
    winshifts_df = pd.DataFrame({})
    avg_winshifts_df = pd.DataFrame({})

    # sort by the required identifying variables
    df.sort_values(sort_cols, inplace=True)

    # assign groups based on subject number
    df['Group'] = df.apply(utils.assign_group, task=task, axis=1)

    if task == 'ActionValue' or task == 'Prob_RL':
        ''' all data for reversal task '''
        # first remove practice sessions and group by subject and session
        df = df.loc[df['Condition'] != 'Practice'] # remove defined practice
        df = df.loc[~df['Condition'].isnull()] # remove empty conditions

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
        df['Learning Confidence'] = df['Learning Confidence']/5

    return df, reversals_df, winshifts_df, avg_winshifts_df


def main():
    """ Main function for grouping and compiling data into a single excel """
    # initialize variables
    trimmed_frames = []

    # get the directory prefix based on the system
    prefix = 'D:/' if platform.system() == 'Windows' else \
        '/media/synapt1x/SCHOOLUSB/'

    # locate the current directory and file location
    dirname = path.split(path.abspath("__file__"))

    # initialize tk window
    root = Tk()
    root.withdraw()

    [data_dirpath, cols, sort_cols, task, get_block] = determine_task(root,
                                                      dirname, prefix)

    # change to data directory
    chdir(data_dirpath)

    # Ask user to identify the output directory and create an excel writer
    output_dirname = get_directory(root, '../Output/', 'Please select '
                                    'the output directory.')
    output_filename = output_dirname + sep + task + '-' + \
                      time.strftime(
        "%d-%m-%y") + '.xlsx'
    excel_writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

    try:
        if task == 'FaceLearning':
            # first merge the learning and recall files
            all_data_df = utils.merge_facelearning(data_dirpath)

            [summary_df, plot_df] = utils.calculate_facelearning_measures(
                all_data_df)
        else:

            # get a list of all data files in data directory chosen
            allFiles = glob.glob("*.xlsx")
            try:
                num_files = len(allFiles)
            except:
                messagebox.showinfo(
                    "No excel spreadsheets found. Please restart the program.")

            # parse over all data files
            for file_name in allFiles:
                # store the dataframe after only selecting necessary columns
                trimmed_frames.append(process_file(file_name, cols, get_block))

            # concatenate the dataframes into one and process it
            output_df = pd.concat(trimmed_frames)

            # recall in face learning task also requires names from the typed excel
            if task == 'FaceLearning-Recall':
                temp_path = prefix + 'MandanaResearch/OCD-FaceLearning' \
                            '/RecallResponses/'
                chdir(temp_path)

                recall_cols = ['Subject', 'Block', 'Trial', 'Recall Choice', 'Recog '
                                'Choice']
                file_name = glob.glob("*.xlsx")[0]
                recall_df = process_file(file_name, recall_cols, False)
                output_df = pd.merge(output_df, recall_df)

            # process the overall dataframe
            [all_data_df, reversals_df, winshifts_df, winshifts_avg_df] = \
                process_dataframe(output_df, task, sort_cols, output_dirname)

        # format and save the output excel file
        all_data_df.to_excel(excel_writer, index=False, sheet_name='All Data')
        if task == 'ActionValue' or task == 'Prob_RL':
            reversals_df.to_excel(excel_writer, index=False,
                                  sheet_name = 'Reversals')
            winshifts_df.to_excel(excel_writer, index=False, header=True,
                                  sheet_name = 'Winshifts')
            winshifts_avg_df.to_excel(excel_writer, index=True, header=True,
                                  sheet_name = 'Avg Winshifts')
        if task == 'FaceLearning':
            summary_df.to_excel(excel_writer, index=False,
                                sheet_name = 'Analysis')
            plot_df.to_excel(excel_writer, index=False,
                                sheet_name = 'Means')
        excel_writer.save()
    except ValueError:
        messagebox.showwarning('Warning', 'No Excel files found in data '
                                          'directory.')
    except IndexError:
        messagebox.showwarning('Warning', 'Data directory is empty.')


if __name__=='__main__':
    main()