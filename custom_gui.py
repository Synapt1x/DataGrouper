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
from tkinter import Tk, Label, Button, Radiobutton, IntVar

def ask_columns(all_cols):
    """ GUI implementation of a window that shows the user all of the 
     columns contained in an excel file, and then asks the user which
     columns they would need. """

    prompt = 'Please select which columns will be necessary'

    root = Tk()
    if prompt:
        Label(root, text=prompt).pack()
    v = IntVar()
    for i, option in enumerate(all_cols):
        Radiobutton(root, text=option, variable=v, value=i).pack(anchor="w")
    Button(text="Submit", command=root.destroy).pack()
    root.mainloop()
    if v.get() == 0: return None
    return options[v.get()]


if __name__ == '__main__':
    pass