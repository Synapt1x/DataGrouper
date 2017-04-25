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
from os import chdir, path, sep

import pandas as pd
import utils
from tkinter import Tk, filedialog, messagebox
import glob, time


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


def process_dataframe(df, task):
    """ Process the data frame for additional calculated columns """

    # first remove practice sessions and group by subject and session
    df = df.loc[df['Condition'] != 'Practice'] # remove defined practice
    df = df.loc[~df['Condition'].isnull()] # remove empty conditions, which is
    # practice in Prob_RL

    df['Group'] = df.apply(utils.assign_group, axis=1)

    # add additional features for analysis
    df['Error Switch'] = utils.determine_error_switches(df, task)

    # add a column for determining the max number of reversals for each subj
    utils.determine_max_reversals(df, task)

    # finally sort by subject and then subsort by session
    #df = df.sort_values(['Subject', 'Session'])

    return df


def output_excel(excel_writer, task):
    """ Add proper formatting and save excel to file """

    # extract refs to workbook and sheet for the output excel
    worksheet = excel_writer.sheets[task]
    workbook = excel_writer.book

    # create center formatting
    center_formatting = workbook.add_format({'align': 'center'})

    # format column widths
    worksheet.set_column('D:D', 4.1, center_formatting)
    worksheet.set_column('F:M', 2.5, center_formatting)
    worksheet.set_column('A:M', None, center_formatting)

    excel_writer.save()


def main():
    """ Main function for grouping and compiling data into a single excel """
    # initialize variables
    output_file = pd.DataFrame({})
    trimmed_frames = []

    # locate the current directory and file location
    dirname = path.split(path.abspath("__file__"))

    # initialize tk window
    root = Tk()
    root.withdraw()

    # Ask user to identify the data directory
    data_dirpath = get_directory(root, dirname, 'Please select the data '
                                               'directory.')
    data_dirname = data_dirpath.split(sep)[-1]

    # Identify the columns for compilation based on which task was chosen
    if (data_dirname == 'ActionValue'):
        cols = ['Subject', 'Session', 'WinningAction[Trial]', 'Proba',
                'WinLose', 'ActionMade', 'Condition', 'Accuracy',
                'RestCount', 'Score[Trial]']
    else:
        cols = ['Subject', 'Session', 'WinningColor[Trial]', 'Proba',
                'WinLose', 'ColorPicked', 'Condition', 'Accuracy',
                'RestCount', 'Score[Trial]']

    # change to data directory
    chdir(data_dirpath)

    # Ask user to identify the output directory and create an excel writer
    output_dirname = get_directory(root, dirname, 'Please select the output '
                                                  'directory.')
    output_filename = output_dirname + sep + data_dirname + '-' + \
                      time.strftime(
        "%d-%m-%y") + '.xlsx'
    excel_writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

    # get a list of all data files in data directory chosen
    allFiles = glob.glob("*.xlsx")
    try:
        num_files = len(allFiles)
    except:
        messagebox.showinfo(
            "No excel spreadsheets found. Please restart the program.")

    # parse over all data files
    for file in allFiles:
        excel = pd.ExcelFile(file)

        # now read excel file data into a DataFrame
        datafile = pd.read_excel(excel, converters={'WinLose':str,
                                                    'Condition':str})

        # store the dataframe after only selecting necessary columns
        trim_datafile = datafile[cols]
        trimmed_frames.append(trim_datafile)

    # concatenate the dataframes into one and process it
    output_file = pd.concat(trimmed_frames)
    output_file = process_dataframe(output_file, data_dirname)

    # format and save the output excel file
    output_file.to_excel(excel_writer, index=False, sheet_name=data_dirname)
    output_excel(excel_writer, data_dirname)


if __name__=='__main__':
    main()


