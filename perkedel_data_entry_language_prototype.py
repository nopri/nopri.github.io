#
# Perkedel
# Simple, spreadsheet-inspired 
# Domain-specific programming language 
# for data entry
# (c) Noprianto <nop@noprianto.com>
# 2017
# GPL
#

import os
import re
import shelve
import sys
import time
import thread
from Tkinter import *
import ttk
import ScrolledText
import tkFont
import tkMessageBox
import tkFileDialog


TITLE = 'Perkedel: spreadsheet-inspired domain-specific programming language for data entry (version 0.1)'
COPYRIGHT = '(c) Noprianto <nop@noprianto.com>, 2017'

REGEX_ID = '^[A-Za-z]+[0-9]+$'
WIDGETS = ['', '_', '#', ',', '-']
T_ASSIGN = '='
T_COMMENT = '/'
T_COMMAND = '>'
T_ALL = [T_ASSIGN, T_COMMENT, T_COMMAND]
SEP_COLUMN = ':'
ID_DATABASE_NAME = 'A0'
ID_APPLICATION_TITLE = 'B0'
ID_DATABASE_OK = 'D0'
ID_DATABASE_ERROR = 'E0'
DATABASE_SUFFIX = '.db'
TEMP_FILE_NAME = 'temp.py'

TITLE_CONFIRM = 'Please Confirm'
TITLE_SYNTAX_ERROR = 'Syntax Error'
ERR_NONE = 'Nothing to run. Do you want to load sample code?'
CONFIRM_SIMPLE = 'Do you want to load the simplified code (without comments)?'
CONFIRM_QUIT = 'Are you sure you want to quit this application?'

SAMPLE = '''
/ Hello
/ This is a simple data entry programming language
/
/ We only have 2 data types:
/ 1. Text
/ 2. Number
/
/ Identifier: 
/ Alphanumeric starting with at least one a-z and at least one 0-9
/ (case-insensitive)
/
/ This is a comment
/ Comment is always line-based
/
/ For example, we want to save the data into a database named: data
/ A0 is a special identifier: name of the database
/ B0 is a special identifier: title of application window
/ D0 is a special identifier: message (when data have been saved)
/ E0 is a special identifier: message (when error occurred)
/ A .db suffix will added to the actual database file
/ = is an assignment
/ Syntax: = Identifier Value 

= A0 data
= B0 Hello World
= D0 Data saved
= E0 Error occurred

/ FUTURE:
/ For example, we want to save into table named: table1
/ C0 is a special identifier: name of the table for command indexed at 0
/ This is an assignment (for a command)
/ However, currently this is reserved/planned for future implementation
/ = C0 data

/ Data entry user interface is always in two columns
/ Label_1 Input_1
/ Label_2 Input_2
/ Label_3 Input_3
/ ...
/ ...
/ Label: Column A
/ Input: Column B
/ Row starting from 1
/
/ For example, we want to set the default value for B2

= B2 My Name

/ And set the default value for B3

= B3 50

/ This is the actual data entry form declaration
Hello World
Name: 
Age: 

/ This is an actual command
/ Command starts with a >, followed by a label
/ Syntax: > Label
> Save

'''

SAMPLE_2 = '''
= A0 data
= B0 Hello World
= D0 Data saved
= E0 Error occurred
= B2 My Name
= B3 50
Hello World
Name: 
Age: 
> Save
'''


modified = False
editor = None
status = None
file_label = None
file_name = None
root = None

symbols = {}
errors = []
form = []

generated_file = os.path.join(os.getcwd(), TEMP_FILE_NAME)


#---------- Valid identifier or type ----------------------------------#
def is_id(s):
    return re.match(REGEX_ID, s, re.I)

def is_type_database_id(s):
    return re.match(REGEX_ID, s, re.I)

def is_type_number(n):
    ret = False
    #
    try:
        float(n)
        ret = True
    except:
        pass
    #
    return ret

def is_type_text(t):
    return True
#----------------------------------------------------------------------#


#---------- Tokenization -----------------------------------------------#
def tokenize(s):
    ret = []
    #
    try:
        s = s.strip()
        ret = s.split()
    except:
        pass
    #
    return ret
#----------------------------------------------------------------------#


#---------- Statement -------------------------------------------------#
def is_text(t):
    ret = False
    #
    try:
        if not t[0] in T_ALL:
            ret = True
    except:
        pass
    #
    return ret

def is_assignment(t):
    ret = False
    #
    try:
        if t[0] == T_ASSIGN and len(t) >= 3:
            ret = True
    except:
        pass
    #
    return ret

def get_assignment(t):
    ret = []
    #
    try:
        t = t.strip()
        t = t.split(None, 2)
        ret = [t[0], t[1], t[2]]
    except:
        pass
    #
    return ret

def is_comment(t):
    ret = False
    #
    try:
        if t[0] == T_COMMENT:
            ret = True
    except:
        pass
    #
    return ret

def is_command(t):
    ret = False
    #
    try:
        if t[0] == T_COMMAND and len(t) >= 2:
            ret = True
    except:
        pass
    #
    return ret

def get_command(t):
    ret = []
    #
    try:
        t = t.strip()
        t = t.split(None, 1)
        ret = [t[0], t[1]]
    except:
        pass
    #
    return ret
#----------------------------------------------------------------------#


#---------- Parser and Code generator ---------------------------------#
def parse(code):
    global symbols, errors, form
    symbols = {}
    errors = []
    form = []
    
    line = 0
    commands = 0
    index = 1
    code = code.split(os.linesep)
    for i in code:
        line += 1
        t = tokenize(i)
        if is_comment(t) or not i.strip():
            continue
        #
        if is_assignment(t):
            temp = get_assignment(i)
            if temp:
                if is_id(temp[1]):
                    symbols[temp[1].upper()] = temp[2]
                else:
                    errors.append('Line %s, assignment error: %s' %(line, i))
        elif is_command(t):
            temp = get_command(i)
            if temp:
                key = 'C%s' %(commands)
                form.append((commands, symbols.get(key), temp[1], '', '', '', key, '', ''))
                commands += 1
            else:
                errors.append('Line %s, command error: %s' %(line, i))
        elif is_text(t):
            cols = i.split(SEP_COLUMN, 1)
            key = 'A%s' %(index)
            if len(cols) >= 2:
                key2 = 'B%s' %(index)
                label = cols[0]
                ui = cols[1].strip()
                default = symbols.get(key)
                default2 = symbols.get(key2)
            else:
                key2 = ''
                label = i
                ui = None
                default = None
                default2 = ''
            index += 1
            form.append(('', '', '', label, ui, default, key, key2, default2))
        else:
            errors.append('Line %s, unknown statement: %s' %(line, i))            
    #
    generate()

def generate():
    if errors:
        sep = os.linesep
        message = sep.join(errors)
        tkMessageBox.showerror(TITLE_SYNTAX_ERROR, message)
        return
    #
    generate_file()
    
def generate_header():
    return 'Generated by %s on %s%s# %s' %(
            sys.argv[0],
            time.asctime(),
            os.linesep,
            COPYRIGHT,
        )

def generate_ui_part(u, row):
    ret = ''
    #
    if not u[0] and not u[1] and not u[2] and not u[7]: #label only
        ret = '''
        %s = Label(text='%s')
        %s.grid(row=%s, column=0, columnspan=2, sticky=W, padx=8, pady=8)
        
        ''' %(u[6], u[3], u[6], row)
    elif not u[0] and not u[1] and not u[2] and u[7]: #label and input
        ret = '''
        %s = Label(text='%s')
        %s.grid(row=%s, column=0, sticky=W, padx=8, pady=8)
        %s = Entry()
        %s.grid(row=%s, column=1, sticky=NSEW, padx=8, pady=8)
        %s.insert(0, '%s')
        vars['%s'] = '%s'
        vars['%s'] = %s
        ''' %(u[6], u[3], u[6], row, u[7], u[7], row, u[7], u[8] or '', 
                u[6], u[5] or u[3], u[7], u[7])    
    elif u[2] and u[6]: #button
        ret = '''
        %s = Button(text='%s', command=save)
        %s.grid(row=%s, column=1, sticky=W, padx=8, pady=8)
        ''' %(u[6], u[2], u[6], row)    
    #
    return ret     

def generate_ui():
    ret = ''
    #
    row = 0
    for i in form:
        ret += generate_ui_part(i, row)
        row += 1
    #
    return ret
    
def generate_file():
    content = """
# %s
# Please do not modify


import re
import shelve
import time
from Tkinter import *
import ttk
import tkMessageBox

symbols = %s
vars = {}

title = symbols.get('%s')

def get_field(s):
    return re.sub('\s', '_', s)

def save():
    db = symbols.get('%s')
    if not db:
        return
    #
    db = db + '%s'
    try:
        d = shelve.open(db)
    except:
        return
    #
    vars2 = {}
    for k in vars.keys():
        vars2[k] = vars[k]
    #
    for k in vars2.keys():
        val = vars2[k]
        if isinstance(val, str):
            vars2[k] = get_field(val)
        else:
            vars2[k] = val.get()
    #
    vars3 = {}
    for k in vars2.keys():
        k0 = k[0]
        k1 = k[1]
        k2 = 'B' + k1
        v = vars2[k]
        if k0 == 'A':
            vars3[v] = vars2[k2]
    #
    key = str(time.time())
    try:
        d[key] = vars3
        d.close()
        msg = symbols.get('%s')
        if msg:
            tkMessageBox.showinfo(title or '', msg)        
    except:
        msg = symbols.get('%s')
        if msg:
            tkMessageBox.showerror(title or '', msg)        
    
def create_ui():
    %s

def main():
    root = Tk()
    root.title(title or '')
    root.resizable(width=False, height=False)
    create_ui()
    root.mainloop()


if __name__ == '__main__':
    main()
""" %(generate_header(), 
        symbols, 
        ID_APPLICATION_TITLE,
        ID_DATABASE_NAME, 
        DATABASE_SUFFIX,
        ID_DATABASE_OK, 
        ID_DATABASE_ERROR, 
        generate_ui())
    open(generated_file, 'w').write(content)
    #
    thread.start_new_thread(run_file, ())
    
#----------------------------------------------------------------------#


#---------- Run file --------------------------------------------------#
def run_file():
    os.system('python %s' %(generated_file))    
#----------------------------------------------------------------------#


#---------- User interface---------------------------------------------#
def run(code):
    global file_name
    
    if not isinstance(code, str):
        code = code.strip()
    else:
        code = ''
    #
    if not code:
        res = tkMessageBox.askquestion(TITLE_CONFIRM, ERR_NONE)
        if res == 'yes':
            res = tkMessageBox.askquestion(TITLE_CONFIRM, CONFIRM_SIMPLE)
            if res == 'yes':
                editor_set(SAMPLE_2)
            else:
                editor_set(SAMPLE)
            reset_modified()
            code = SAMPLE
    #
    if code:
        parse(code)

def confirm_quit():
    res = tkMessageBox.askquestion(TITLE_CONFIRM, CONFIRM_QUIT)
    if res == 'yes':
        file_new()
        root.destroy()
            
def editor_modified(e):
    global modified
    #
    modified = True
    status['text'] = 'Modified'
    editor.edit_modified(0)

def editor_clear():
    editor.delete('1.0', END)
    reset_modified()

def editor_set(t):
    editor.insert('1.0', t)
    
def editor_get():
    return editor.get('1.0', END)

def reset_modified():
    global modified
    #
    modified = False
    status['text'] = '' 
    file_label['text'] = ''
    editor.edit_modified(0)

def file_new():
    if modified:
        res = tkMessageBox.askquestion('New', 'Editor is modified. Do you want to save to content?', icon='warning')
        if res == 'yes':
            if not file_name:
                f = tkFileDialog.asksaveasfile(mode='w')
            else:
                f = open(file_name, 'w')
            if f:
                text = editor_get()
                f.write(text)
                f.close()
    #
    editor_clear()

def file_open():
    global modified, file_name
    #
    file_new()
    #
    f = tkFileDialog.askopenfilename()
    if f:
        text = open(f).read()
        editor_set(text)
        reset_modified()
        file_name = f
        file_label['text'] = file_name

def file_save():
    global file_name
    #
    if modified:
        if not file_name:
            f = tkFileDialog.asksaveasfile(mode='w')
            if f: 
                file_name = f.name
        else:
            f = open(file_name, 'w')
        if f:
            text = editor_get()
            f.write(text)
            f.close()
            reset_modified()
            file_label['text'] = file_name
        
def file_run():
    text = editor_get()
    run(text)

def file_view():
    f = tkFileDialog.askopenfilename()
    if f:
        window = Toplevel(root)
        text = ScrolledText.ScrolledText(window)
        text.pack(fill='both')
        #
        d = shelve.open(f)
        c = ''
        counter = 0
        for k in d.keys():
            counter += 1
            c += k
            c += ': '
            c += str(d[k])
            c += os.linesep
        d.close()
        #
        text.insert('1.0', c)
        text['state'] = 'disabled'
        label = Label(window, text='Records: %s' %(counter))
        label.pack(fill='x')
    
def create_ui():
    global editor, status, file_label
    #
    font = tkFont.Font(family='Courier', size=12)
    #
    new_button = Button(text='New', command=file_new)
    new_button.grid(row=0, column=0, sticky=NSEW)
    #
    open_button = Button(text='Open', command=file_open)
    open_button.grid(row=0, column=1, sticky=NSEW)
    #
    save_button = Button(text='Save', command=file_save)
    save_button.grid(row=0, column=2, sticky=NSEW)
    #
    run_button = Button(text='Run', command=file_run)
    run_button.grid(row=0, column=3, sticky=NSEW)
    #
    view_button = Button(text='View Data', command=file_view)
    view_button.grid(row=0, column=4, sticky=NSEW)
    #
    editor = ScrolledText.ScrolledText(wrap='none',font=font)
    editor.bind('<<Modified>>', editor_modified)
    editor.grid(row=1, column=0, columnspan=5, rowspan=10, sticky=NSEW)
    #
    file_label = Label(text='')
    file_label.grid(row=11, column=0, columnspan=4, sticky=W)
    #
    status = Label(text='')
    status.grid(row=11, column=4, sticky=W)
    
def main():
    global root 
    #
    root = Tk()
    root.title(TITLE)
    root.resizable(width=False, height=False)
    create_ui()
    root.protocol('WM_DELETE_WINDOW', confirm_quit)
    root.mainloop()
#----------------------------------------------------------------------#


if __name__ == '__main__':
    main()
