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
import processing
from tkinter import Tk, messagebox
from custom_gui import ask_columns
import glob, time
import platform


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

    [data_dirpath, cols, sort_cols, task, get_block] = \
        processing.determine_task(root, dirname, prefix)

    # change to data directory
    chdir(data_dirpath)

    # Ask user to identify the output directory and create an excel writer
    output_dirname = processing.get_directory(root, '../Output/', 'Please '
                                                                  'select '
                                                                  'the '
                                                                  'output '
                                                                  'directory')
    output_filename = output_dirname + sep + task + '-'  + time.strftime(
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
            all_files = glob.glob("*.xlsx")
            if not len(all_files):
                messagebox.showwarning("Warning", "No excel spreadsheets "
                                                  "found. Please restart "
                                                  "the program and try again.")

            # if columns have not been specified yet call process example to
            # get info
            if not cols:
                # setup the excel file
                excel = pd.ExcelFile(all_files[0])

                # now read excel file data into a DataFrame
                datafile = pd.read_excel(excel)
                # assign cols
                cols = ask_columns(list(datafile.columns.values))

            # print which columns will be pulled into the output excel
            print("Current columns to be captured from the excel files:\n")
            for col in cols: print(col)

            # parse over all data files
            for file_name in all_files:
                # store the data frame after only selecting necessary columns
                trimmed_frames.append(processing.process_file(file_name, cols,
                                                    get_block))

            # concatenate the data frames into one and process it
            output_df = pd.concat(trimmed_frames)

            # recall in face learning task also needs names from the typed
            # excel
            if task == 'FaceLearning-Recall':
                temp_path = prefix + 'MandanaResearch/OCD-FaceLearning' \
                            '/RecallResponses/'
                chdir(temp_path)

                recall_cols = ['Subject', 'Block', 'Trial', 'Recall Choice',
                               'Recog Choice']
                file_name = glob.glob("*.xlsx")[0]
                recall_df = processing.process_file(file_name, recall_cols,
                                                  False)
                output_df = pd.merge(output_df, recall_df)

            # process the overall dataframe
            [all_data_df, reversals_df, winshifts_df, winshifts_avg_df] = \
                processing.process_dataframe(output_df, task, sort_cols,
                                     output_dirname)

        # format and save the output excel file
        all_data_df.to_excel(excel_writer, index=False, sheet_name='All Data')
        if task == 'ActionValue' or task == 'Prob_RL':
            reversals_df.to_excel(excel_writer, index=False,
                                  sheet_name='Reversals')
            winshifts_df.to_excel(excel_writer, index=False, header=True,
                                  sheet_name='Winshifts')
            winshifts_avg_df.to_excel(excel_writer, index=True, header=True,
                                  sheet_name='Avg Winshifts')
        if task == 'FaceLearning':
            summary_df.to_excel(excel_writer, index=False,
                                sheet_name='Analysis')
            plot_df.to_excel(excel_writer, index=False,
                                sheet_name='Means')
        excel_writer.save()

    except ValueError:
        messagebox.showwarning('Warning', 'No Excel files found in data '
                                          'directory.')
    except IndexError:
        messagebox.showwarning('Warning', 'Data directory is empty.')

    except KeyError:
        messagebox.showwarning('Warning', 'Chosen column not found in '
                                          'current excel file.')


if __name__ == '__main__':
    main()
