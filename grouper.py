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
        if (num_errors > 2):
            result = messagebox.askyesno(title="Quit?", message="No "
                                                                "directory \
   selected over multipled attempts. Do you want to quit instead?")
            if (result == True):
                print("Exiting program...")
                exit()
            else:
                num_errors = 0
                break
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
    df['Choice'] = utils.determine_choice_made(df, task)
    df['Error Switch'] = utils.determine_error_switches(df, task)

    return df


def main():
    # initialize variables
    output_file = pd.DataFrame({})
    trimmed_frames = []
    cols = ['Subject', 'Session', 'WinningAction[Trial]', 'Proba',
            'WinLose', 'XPosition', 'Condition', 'Accuracy', 'CountTrial']

    # locate the current directory and file location
    dirname = path.split(path.abspath("__file__"))

    # initialize tk window
    root = Tk()
    root.withdraw()

    # Ask user to identify the data directory
    # dataDirpath = get_directory(root, dirname, 'Please select the data
    # directory.')
    # temporary while testing
    dataDirpath = path.dirname(
        '/home/synapt1x/MandanaResearch/OCD-ReversalLearning/ReversalLearning'
        '-ExcelFiles/ActionValue/')
    dataDirname = dataDirpath.split(sep)[-1]

    # change to data directory
    chdir(dataDirpath)

    # Ask user to identify the output directory and create an excel writer
    outputDirname = get_directory(root, dirname, 'Please select the '
                                                     'output directory.')
    outputFilename = outputDirname + sep + dataDirname + '-' + time.strftime(
        "%d-%m-%y") + '.xlsx'
    excel_writer = pd.ExcelWriter(outputFilename)


    # get a list of all data files in data directory chosen
    allFiles = glob.glob("*.xlsx")
    try:
        numFiles = len(allFiles)
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

    output_file = process_dataframe(output_file, dataDirname)


    output_file.to_excel(excel_writer, sheet_name=dataDirname)


if __name__=='__main__':
    main()


