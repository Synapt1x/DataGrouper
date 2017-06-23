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
from tkinter import Tk, Label, Listbox, Button
#Button, Radiobutton, IntVar

def ask_columns(all_cols):
    """ GUI implementation of a window that shows the user all of the 
     columns contained in an excel file, and then asks the user which
     columns they would need. """

    # set the display message
    prompt = 'Please select which columns will be necessary for the output ' \
             'excel file.'

    # create the root window and add label to top of window
    window = Tk()
    Label(window, text=prompt,
          width=35,
          wraplength=150,
          justify='center').pack()

    # create list box
    listbox = Listbox(window,
                      selectmode='multiple',
                      exportselection=0)
    # add column names to the list box
    for col_name in all_cols:
        listbox.insert(all_cols.index(col_name), col_name)
    listbox.pack()

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


if __name__ == '__main__':
    pass