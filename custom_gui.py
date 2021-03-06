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
from tkinter import Tk, Label, Listbox, Button, Scrollbar, Frame, \
    Radiobutton, IntVar
#Button, Radiobutton


class AskColumns:

    def __init__(self, master, all_cols):

        self.master = master
        self.master.deiconify()
        self.frame = Frame(self.master)
        self.all_cols = all_cols

        self.prompt = 'Please select which columns will be necessary for ' \
                      'the output excel file.'
        self.label = Label(master, text=self.prompt,
                           width=35,
                           wraplength=150,
                           justify='center').pack()
        self.add_listbox()
        '''submit_button = Button(self,
                               text='Submit',
                               command=self.update_vals())
        submit_button.pack()'''
        self.frame.pack()

    def add_listbox(self):

        self.listbox_frame = Frame(self.master)

        # create a scroll bar for the list box
        scrollbar = Scrollbar(self.listbox_frame)
        scrollbar.pack(side='right', fill='y')

        # create list box
        self.listbox = Listbox(self.listbox_frame,
                               selectmode='multiple',
                               exportselection=0)
        # add column names to the list box
        for col_name in self.all_cols:
            self.listbox.insert(self.all_cols.index(col_name), col_name)
        self.listbox.pack(side='left', fill='y')

        # pack the listbox
        self.listbox_frame.pack()

        # attach listbox to scrollbar
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

    def update_vals(self):

        chosen_lines = self.listbox.curselection()
        cols = [self.all_cols[line] for line in chosen_lines]

        self.master.quit()

        return cols


class AskProcessing:

    def __init__(self, master):

        self.master = master
        self.frame = Tk.Frame(self.master)
        self.quitButton = Tk.Button(self.frame, text='Quit', width=25,
                                    command=self.close_windows)
        self.quitButton.pack()
        self.frame.pack()

    def close_windows(self):

        self.master.destroy()


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
    columns_window = Tk()
    columns_window.resizable(0, 0)  # prevent resizing of the box

    Label(columns_window, text=prompt,
          width=35,
          wraplength=150,
          justify='center').pack()

    # create frame for the listbox and scrollbar
    listbox_frame = Frame(columns_window)

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

    # add a submit button1
    submit_button = Button(columns_window,
                           text='Submit',
                           command=columns_window.quit)
    submit_button.pack()

    columns_window.mainloop()

    # ---------------- End of listbox gui specification

    # acquire the chosen columns
    chosen_lines = listbox.curselection()
    cols = [all_cols[line] for line in chosen_lines]

    # destroy the window after acquiring the necessary information
    columns_window.destroy()

    return cols


def choose_operations(available_funcs):
    """ GUI implementation of a window that displays to the user possible
    calculation functions for processing the current set of data.
    
    :param: available_funcs:
            a list of tuples of the form (name, function_handle), where name
            and function_handle refer to all of the functions defined in 
            the utils.py file.
    
    :return:
    
    """
    # initialize list of chosen functions
    chosen_funcs = []

    # set the display message
    prompt = 'Please select which operations will be performed on the input ' \
             'datasets.'

    # create the root window and add label to top of window
    operations_window = Tk()
    operations_window.resizable(0, 0)  # prevent resizing of the box

    Label(operations_window, text=prompt,
          width=35,
          wraplength=150,
          justify='center').pack()

    val = IntVar()

    Radiobutton(operations_window,
                text='test me',
                indicatoron=0,
                width=20,
                padx=20,
                variable=val).pack()

    return chosen_funcs


if __name__ == '__main__':
    pass
