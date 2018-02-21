#!/usr/bin/env python
#
#
# generate-ui-spreadsheet-frontend.py
#
# (c) Noprianto <nop@noprianto.com>
# 2017
# License: GPL


import os
import webbrowser
from Tkinter import *
from tkFileDialog import askopenfilename
import ttk
import ScrolledText

import openpyxl

import generate_ui_spreadsheet as module


TITLE = 'Pangsit User Interface Code Generator'
PADDING = 10
MAX_ROW = 10
MAX_COL = 10


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.resizable(width=False, height=False)
        self.master.rowconfigure(MAX_ROW)
        self.master.columnconfigure(MAX_COL)
        self.create_ui()
        self.t = None
        self.o = None

    def create_ui(self):
        label_output = Label(text='Available platform: ')
        label_output.grid(column=0, row=0, padx=PADDING, pady=PADDING,
            sticky=W)
        column = 0
        for t in module.TYPE.keys():
            button = Button(text=t, command=lambda t=t: self.generate(t))
            button.grid(column=column, row=1, padx=PADDING, pady=PADDING)
            column += 1
        label_input = Label(text='Input file: ')
        label_input.grid(column=0, row=2, padx=PADDING, pady=PADDING,
            columnspan=MAX_COL, sticky=W)
        self.label_input_2 = Label()
        self.label_input_2.grid(column=1, row=2, padx=PADDING, pady=PADDING,
            columnspan=MAX_COL, sticky=W)
        label_output = Label(text='Generated code: ')
        label_output.grid(column=0, row=3, padx=PADDING, pady=PADDING,
            columnspan=MAX_COL, sticky=W)
        self.label_output_2 = Label()
        self.label_output_2.grid(column=1, row=3, padx=PADDING, pady=PADDING,
            columnspan=MAX_COL, sticky=W)
        self.text = ScrolledText.ScrolledText()
        self.text.grid(column=0, row=4, columnspan=MAX_COL,
            padx=PADDING, pady=PADDING)
        self.run_button = Button(text='Run', command=self.run)
        self.run_button.grid(column=0, row=5, padx=PADDING, pady=PADDING,
            sticky=W)

    def generate(self, t):
        f = askopenfilename()
        if f:
            self.label_input_2['text'] = f

            try:
                book = openpyxl.load_workbook(f)
            except Exception, e:
                self.text.insert(INSERT, e)
                return
            #
            output_file = '%s%s' %(
                os.path.splitext(f)[0], module.TYPE.get(t)[0])
            #

            self.o = output_file
            self.t = t

            self.label_output_2['text'] = output_file
            module.generate(book, t, output_file)
            self.text.delete('1.0', END)
            self.text.insert(INSERT, open(output_file).read())

    def run(self):
        if self.t == 'python-tk':
            os.system('python %s' %(self.o))
        elif self.t == 'html':
            webbrowser.open(self.o)


def main():
    app = Application()
    app.master.title(TITLE)
    app.mainloop()


if __name__ == '__main__':
    main()
