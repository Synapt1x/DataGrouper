"""
Data Grouper custom gui functions
============================
Created by: Chris Cadonic
For: Utility in Dr. Mandana Modirrousta's Lab
----------------------------
This file contains code for :

Implementing custom GUI modules for specific purposes in the general-use 
grouper.py function.

============================

"""
from tkinter import Tk, Label, Listbox, Button, Scrollbar, Frame
#Button, Radiobutton, IntVar

def ask_columns(all_cols):
    """ GUI implementation of a window that shows the user all of the 
     columns contained in an excel file, and then asks the user which
     columns they would need. 
     
    :param all_cols:
        input list of all columns to be displayed for the user to select
    
    :return:
     
     """

    # set the display message
    prompt = 'Please select which columns will be necessary for the output ' \
             'excel file.'

    # create the root window and add label to top of window
    window = Tk()
    window.resizable(0, 0)  # prevent resizing of the box

    Label(window, text=prompt,
          width=35,
          wraplength=150,
          justify='center').pack()

    # create frame for the listbox and scrollbar
    listbox_frame = Frame(window)

    # create a scroll bar for the list box
    scrollbar = Scrollbar(listbox_frame)
    scrollbar.pack(side='right', fill='y')

    # create list box
    listbox = Listbox(listbox_frame,
                      selectmode='multiple',
                      exportselection=0)
    # add column names to the list box
    for col_name in all_cols:
        listbox.insert(all_cols.index(col_name), col_name)
    listbox.pack(side='left', fill='y')

    # pack the listbox
    listbox_frame.pack()

    # attach listbox to scrollbar
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    # add a submit button
    submit_button = Button(window,
                           text='Submit',
                           command=window.quit)
    submit_button.pack()

    window.mainloop()

    # ---------------- End of listbox gui specification

    # acquire the chosen columns
    chosen_lines = listbox.curselection()
    cols = [all_cols[line] for line in chosen_lines]

    return cols


def choose_operations():
    """ GUI implementation of a window that displays to the user possible
    calculation functions for processing the current set of data.
    
    :param:
    
    :return:
    
    """


if __name__ == '__main__':
    pass