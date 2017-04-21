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
import numpy as np
import utils
from tkinter import Tk, filedialog, messagebox
import glob, time

def get_directory(root, initial_dir, title_dir):
    num_errors = 0
    while True:
        if (num_errors > 0):
            print("Exiting program...")
            exit()
        try:
            get_dirname = filedialog.askdirectory(
                parent=root, initialdir=initial_dir,
                title=title_dir)
            if not get_dirname:
                raise ValueError("empty string")
            break
        except ValueError:
            num_errors += 1
            messagebox.showinfo("Invalid directory - Failed \
    attempt %0.0f/5" % num_errors, "Please select a valid directory...")
    return get_dirname


def process_dataframe(df, task):
    # first remove practice sessions and group by subject and session
    df = df.loc[df['Condition'] != 'Practice']
    df = df.sort_values(['Subject', 'Session'])

    # Add additional features for analysis
    if task == 'ActionValue':
        df['Choice'] = utils.determine_choice_made(df)
    df['Error Switch'] = utils.determine_error_switches(df, task)

    return df


def main():
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
                'WinLose', 'XPosition', 'Condition', 'Accuracy', 'CountTrial',
                'Score']
    else:
        cols = ['Subject', 'Session', 'WinningColor[Trial]', 'Proba',
                'WinLose', 'ColorPicked', 'Card1.RESP', 'Condition',
                'Accuracy', 'CountTrial[Trial]', 'Score[Trial]']

    # change to data directory
    chdir(data_dirpath)

    # Ask user to identify the output directory and create an excel writer
    output_dirname = get_directory(root, dirname, 'Please select the '
                                                     'output directory.')
    output_filename = output_dirname + sep + data_dirname + '-' + \
                      time.strftime(
        "%d-%m-%y") + '.xlsx'
    excel_writer = pd.ExcelWriter(output_filename)

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

    # concatenated dataframe
    output_file = pd.concat(trimmed_frames)
    output_file = process_dataframe(output_file, data_dirname)
    output_file.to_excel(excel_writer, sheet_name=data_dirname)


if __name__=='__main__':
    main()


