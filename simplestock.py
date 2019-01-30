#!/usr/bin/env python
#
#
# simplestock
# Very simple stock control application
# (c) Noprianto <nop@noprianto.com>
# 2008-2009, 2017
# http://github.com/nopri/code
# License: GPL
# Version: 1.00
#
#
# Note:
# - Single python script (simplestock.py) since version 0.99
# - Database structure changed in version 0.99
# - Dependency check removed in version 0.99
#
# Maintenance:
# - No longer maintained since version 1.00 (moved to code repo)
#
#

import sys
import os
try:
   from hashlib import md5 as md5new
except ImportError:
   from md5 import new as md5new
import time
import csv


import locale
import webbrowser


try:
    import sqlite3
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gobject
    gobject.threads_init()  #for multithreading
except Exception, e:
    sys.exit(e)


#----------------------------------------------------------------------#
# db_sqlite3.py                                                        #
#----------------------------------------------------------------------#
def db_query(query, args, dbfile):
    ret_data = []
    ret = []
    try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute(query, args)
        ret_data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        ret = [0, ret_data, cur.lastrowid]
    except Exception, e:
        ret = [2, e.message, None]
    #
    return ret

def db_query_transact(query_args, dbfile):
    ret_data = []
    ret = []
    try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        for q in query_args:
            query = q[0]
            args = q[1]
            cur.execute(query, args)
            ret_data = cur.fetchall()
            ret = [0, ret_data, cur.lastrowid]
    except Exception, e:
        conn.rollback()
        ret = [2, e.message, None]
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()

    #
    return ret


#----------------------------------------------------------------------#
# gtkutils.py                                                          #
#----------------------------------------------------------------------#
#-------------------------------DIALOGS--------------------------------#
def input(title='', label='Input', default='', password=False,
    parent=None, flags=0):
    d = gtk.Dialog(title, parent, flags)
    d.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
    d.add_button(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
    #
    lbl_input = gtk.Label(label)
    ent_input = gtk.Entry()
    ent_input.set_text(default)
    ent_input.select_region(0, -1)
    if password:
        ent_input.set_visibility(False)
    #
    hb = gtk.HBox(False)
    hb.pack_start(lbl_input, padding=10, expand=False)
    hb.pack_start(ent_input, padding=10)
    #
    d.vbox.pack_start(hb, padding=20)
    d.vbox.show_all()
    #
    ret = ''
    dret = d.run()
    #
    if dret == gtk.RESPONSE_ACCEPT:
        ret = ent_input.get_text()
    #
    d.destroy()
    return ret


def __box(type, title, message, modal, parent, flags, buttons,
    message2, image):
    #
    if modal:
        flags += gtk.DIALOG_MODAL
    #
    d = gtk.MessageDialog(parent=parent, flags=flags, type=type,
        buttons=buttons)
    #
    d.set_markup(message)
    d.format_secondary_markup(message2)
    d.set_title(title)
    if image:
        image.show()
        d.set_image(image)
    dret = d.run()
    #
    d.destroy()
    ret = dret
    return ret


def info(title='', message='Information!', modal=True,
    parent=None, flags=0, buttons=gtk.BUTTONS_OK, message2='',
    image=None):
    ret = __box(type=gtk.MESSAGE_INFO,
        title=title, message=message, modal=modal,
        parent=parent, flags=flags, buttons=buttons,
        message2=message2, image=image)
    return ret


def warning(title='', message='Warning!', modal=True,
    parent=None, flags=0, buttons=gtk.BUTTONS_OK, message2='',
    image=None):
    ret = __box(type=gtk.MESSAGE_WARNING,
        title=title, message=message, modal=modal,
        parent=parent, flags=flags, buttons=buttons,
        message2=message2, image=image)
    return ret


def error(title='', message='Error!', modal=True,
    parent=None, flags=0, buttons=gtk.BUTTONS_OK, message2='',
    image=None):
    ret = __box(type=gtk.MESSAGE_ERROR,
        title=title, message=message, modal=modal,
        parent=parent, flags=flags, buttons=buttons,
        message2=message2, image=image)
    return ret


def confirm(title='', message='Confirm?', modal=True,
    parent=None, flags=0, buttons=gtk.BUTTONS_OK_CANCEL, message2='',
    image=None):
    ret = __box(type=gtk.MESSAGE_QUESTION,
        title=title, message=message, modal=modal,
        parent=parent, flags=flags, buttons=buttons,
        message2=message2, image=image)
    return ret
#----------------------------END-OF-DIALOGS----------------------------#

#----------------------------LOGIN DIALOGS-----------------------------#
def simple_login(validator, title='Login', username_label='User Name',
    password_label='Password', parent=None,
    error_message='Authentication Failed.', use_md5=True):
    tryagain = True
    while tryagain:
        uname = ''
        login_status = False
        #
        d = gtk.Dialog(title, parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        tbl = gtk.Table(2, 3)
        #
        ent_uname = gtk.Entry()
        lbl_uname = gtk.Label(username_label)
        lbl_uname.set_alignment(0, 0.5)
        tbl.attach(lbl_uname, 0, 1, 0, 1, xpadding=8, ypadding=8)
        tbl.attach(ent_uname, 1, 3, 0, 1, xpadding=8, ypadding=8)

        ent_passwd = gtk.Entry()
        ent_passwd.set_visibility(False)
        lbl_passwd = gtk.Label(password_label)
        lbl_passwd.set_alignment(0, 0.5)
        tbl.attach(lbl_passwd, 0, 1, 1, 2, xpadding=8, ypadding=8)
        tbl.attach(ent_passwd, 1, 3, 1, 2, xpadding=8, ypadding=8)

        vb = gtk.VBox()
        vb.pack_start(tbl, padding=10)

        d.vbox.pack_start(vb)
        d.vbox.show_all()

        ret = d.run()

        if ret == gtk.RESPONSE_ACCEPT:
            uname = ent_uname.get_text()
            passwd = ent_passwd.get_text()
            if use_md5:
                passwd2 = md5new(passwd).hexdigest()
            else:
                passwd2 = passwd

            if validator(uname, passwd2):
                login_status = True
                tryagain = False
            else:
                login_status = False
                tryagain = True
        else:
            login_status = False
            tryagain = False
        #
        d.destroy()
        if not login_status and tryagain:
            error(title='Error', message=error_message, parent=d)

    return (login_status, uname)


#----------------------------END-OF-LOGIN DIALOGS----------------------#


#-------------------------------HELP WINDOW----------------------------#
def tips(caption, tip, width=200, height=200, parent=None):
    w = gtk.Window(gtk.WINDOW_POPUP)
    w.set_transient_for(parent)
    w.set_position(gtk.WIN_POS_MOUSE)
    w.set_size_request(width, height)
    #
    caption2 =  '<b>%s</b>' %(caption)
    lbl_caption = gtk.Label()
    lbl_caption.set_markup(caption2)
    #
    textb = gtk.TextBuffer()
    textb.set_text(tip)
    textv = gtk.TextView(textb)
    textv.set_editable(False)
    #
    scrollw = gtk.ScrolledWindow()
    scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scrollw.add(textv)
    #
    btn_close = gtk.Button(stock=gtk.STOCK_CLOSE)
    btn_close.connect('clicked', lambda x: w.destroy())
    #
    vbox = gtk.VBox()
    vbox.pack_start(lbl_caption, expand=False, padding=8)
    vbox.pack_start(scrollw, expand=True, padding=8)
    vbox.pack_start(btn_close, expand=False, padding=8)
    hbox = gtk.HBox()
    hbox.pack_start(vbox, padding=8)
    #
    w.add(hbox)
    w.show_all()
#-----------------------------END-OF-HELP WINDOW-----------------------#

#-------------------------------PROPERTY EDITOR------------------------#
class SimplePropertyEditor:
    def __init__(self, property_label='Property', value_label='Value',
        property_width=120, value_width=160):
        self.property_label = property_label
        self.value_label = value_label
        self.property_width = property_width
        self.value_width = value_width
        #
        self.model = gtk.ListStore(str, str)
        self.treeview = gtk.TreeView(self.model)
        self.scrolledwin = gtk.ScrolledWindow()
        self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,
            gtk.POLICY_AUTOMATIC)
        self.scrolledwin.add(self.treeview)
        #
        trvcol_prop = gtk.TreeViewColumn(self.property_label)
        trvcol_prop.set_min_width(self.property_width)
        trvcol_val = gtk.TreeViewColumn(self.value_label)
        trvcol_val.set_min_width(self.value_width)
        cell_prop = gtk.CellRendererText()
        cell_val = gtk.CellRendererText()
        cell_val.set_property('editable', True)
        cell_val.connect('edited', self.__edited)
        trvcol_prop.pack_start(cell_prop, True)
        trvcol_prop.set_attributes(cell_prop, text=0)
        self.treeview.append_column(trvcol_prop)
        trvcol_val.pack_start(cell_val, True)
        trvcol_val.set_attributes(cell_val, text=1)
        self.treeview.append_column(trvcol_val)
        #
        self.clear()
        #

    def __edited(self, cell, path, new_text):
        iter = self.model.get_iter(path)
        self.model.set_value(iter, 1, new_text)

    def clear(self):
        self.model.clear()

    def fill(self, data):
        self.clear()
        if data:
            for p in data:
                self.model.append(p)

#--------------------------END-OF-PROPERTY EDITOR----------------------#


#----------------------------------------------------------------------#
# utils.py                                                             #
#----------------------------------------------------------------------#
def string_sep_rebuild(str, separator=',', remove_space=True,
    unique=True, replace_underscore_with_space=True):
    str = str.strip()
    splitted = str.split(separator)
    splitted2 = [x.strip() for x in splitted]
    if remove_space:
        splitted3 = [x.replace(' ', '') for x in splitted2]
    else:
        splitted3 = splitted2

    if unique:
        splitted4 = []
        for i in splitted3:
            if i not in splitted4:
                splitted4.append(i)
    else:
        splitte4 = splitted3

    if replace_underscore_with_space:
        splitted5 = [x.replace('_', ' ') for x in splitted4]
    else:
        splitted5 = splitted4

    newlist = []
    for part in splitted5:
        if part:
            newlist.append(part)
    ret = separator.join(newlist)
    return ret


def number_format(number, places=0, lang='en_US'):
    locale.setlocale(locale.LC_ALL, lang)
    formatted = locale.format('%.*f', (places, number), True, True)
    return formatted


#----------------------------------------------------------------------#
# application.py                                                       #
#----------------------------------------------------------------------#
class Application:
    def __init__(self):
        #basic properties
        self.name = 'SimpleStock'
        self.version = (0, 99)
        self.version_str = '.'.join([str(x) for x in self.version])
        self.website = 'http://www.noprianto.com'
        self.authors = ('Noprianto <nop@noprianto.com>',)
        self.year = ('2008-2009', '2017')
        self.year_str = ','.join([str(x) for x in self.year])
        self.copyright_str = '(c) %s %s' %(self.year_str, ', '.join(self.authors))
        self.main_title = '%s %s' %(self.name, self.version_str)
        #
        #date time format
        self.date_time_format = '%a, %d %b %Y - %H:%M:%S'
        self.time_format = '%H:%M:%S'
        self.date_format = '%a, %d %b %Y'
        #
        #directories, database
        self.datadir = os.curdir
        self.database = os.path.join(self.datadir,  'data.db')
        #
        #screen related
        screen_width = int(gtk.gdk.screen_width() * 0.8)
        screen_height = int(gtk.gdk.screen_height() * 0.7)
        if screen_width <= 640:
            self.main_win_width = 620
        else:
            self.main_win_width = screen_width
        #
        if screen_height <= 480:
            self.main_win_height = 420
        else:
            self.main_win_height = screen_height
        #
        #tabs, user interface, resources
        #
        self.tabs = ( ('User', gtk.STOCK_HOME),
                      ('Product', gtk.STOCK_FILE),
                      ('Change Password', gtk.STOCK_PREFERENCES),
                      ('About', gtk.STOCK_ABOUT),
                    )
        self.resource_all = [x[0].upper() for x in self.tabs]
        self.resource_all_str = ','.join(self.resource_all)
        #


    def init_db_query(self):
        ret = []
        #groups
        query = '''
        CREATE TABLE groups(id integer primary key autoincrement,
        group_name text, resources text)
        '''
        ret.append(query)
        #
        query = '''
        INSERT INTO groups(group_name, resources)
            VALUES('ADMIN', '%s')
        ''' %(self.resource_all_str)
        ret.append(query)
        #

        #users
        query = '''
        CREATE TABLE users(id integer primary key autoincrement,
        user_name text, real_name text, gid integer references
        groups(id), password text)
        '''
        ret.append(query)
        #
        passwd = 'admin'
        passwd_md5 = md5new(passwd).hexdigest()
        query = '''
        INSERT INTO users(user_name, real_name, gid, password)
            VALUES('admin', 'Administrator', 1, '%s')
        ''' %(passwd_md5)
        ret.append(query)
        #

        #categories
        query = '''
        CREATE TABLE categories(id integer primary key autoincrement,
        category_name text, note text)
        '''
        ret.append(query)
        #

        #units
        query = '''
        CREATE TABLE units(id integer primary key autoincrement,
        unit_name text, note text)
        '''
        ret.append(query)
        #

        #products
        query = '''
        CREATE TABLE products(id text primary key,
        product_name text, price real, uid integer references units(id),
        cid integer references categories(id), stock integer, minstock integer)
        '''
        ret.append(query)
        #

        #products flow
        query = '''
        CREATE TABLE moves(id integer primary key autoincrement,
        dateinfo text,
        user text,
        pid text references products(id),
        move_type text, amount integer, note text)
        '''
        ret.append(query)
        #


        return ret


#----------------------------------------------------------------------#
# ui_about.py                                                          #
# should provide at least: create_ui and reset_ui method               #
# create_ui() should return container                                  #
#----------------------------------------------------------------------#
class UIAbout:
    def __init__(self, app, parent=None):
        self.version = (0, 1, 3)
        self.name = 'UI About Module'
        self.info = '(c) Noprianto, 2009'
        self.app = app
        self.parent = parent

        self.vbox = gtk.VBox()
        self.width = self.app.main_win_width
        self.height = self.app.main_win_height

    def create_ui(self):
        pango_app_name = '''<span weight='ultrabold' font_desc='Courier 14'>%s</span>''' %(self.app.name)
        lbl_name = gtk.Label()
        lbl_name.set_markup(pango_app_name)
        lbl_name.set_alignment(0, 0.5)
        lbl_ver = gtk.Label(self.app.version_str)
        lbl_ver.set_alignment(0, 0.5)
        lbl_copy = gtk.Label(self.app.copyright_str)
        lbl_copy.set_alignment(0, 0.5)
        btn_web = gtk.Button('Visit noprianto.com')
        btn_web.connect('clicked', self.go_website)
        #
        vbox_info = gtk.VBox()
        vbox_info.pack_start(lbl_name, expand=False, padding=4)
        vbox_info.pack_start(lbl_ver, expand=False, padding=4)
        vbox_info.pack_start(lbl_copy, expand=False, padding=4)
        vbox_info.pack_start(btn_web, expand=False, padding=8)
        #
        hbox = gtk.HBox()
        hbox.pack_start(vbox_info, expand=False, padding=10)
        #
        self.vbox.pack_start(hbox, padding=40)
        return self.vbox

    def reset_ui(self):
        pass

    def go_website(self, widget):
        webbrowser.open_new(self.app.website)


#----------------------------------------------------------------------#
# ui_password.py                                                       #
# should provide at least: create_ui and reset_ui method               #
# create_ui() should return container                                  #
#----------------------------------------------------------------------#
class UIPassword:
    def __init__(self, app, parent=None, myuid=0, myname=''):
        self.version = (0, 2, 5)
        self.name = 'UI Change Password Module'
        self.info = '(c) Noprianto, 2009'
        self.app = app
        self.parent = parent
        self.myuid = myuid
        self.myname = myname

        self.vbox = gtk.VBox()
        self.width = self.app.main_win_width
        self.height = self.app.main_win_height

    def create_ui(self):
        lbl_old = gtk.Label('Current Password')
        lbl_old.set_alignment(0, 0.5)
        self.ent_old = gtk.Entry()
        self.ent_old.set_visibility(False)
        lbl_new = gtk.Label('New Password')
        lbl_new.set_alignment(0, 0.5)
        self.ent_new = gtk.Entry()
        self.ent_new.set_visibility(False)
        lbl_again = gtk.Label('New Password (again)')
        lbl_again.set_alignment(0, 0.5)
        self.ent_again = gtk.Entry()
        self.ent_again.set_visibility(False)
        #
        btn_change = gtk.Button('_Change password')
        btn_change.connect('clicked', self.passwd_change)
        img_change = gtk.Image()
        img_change.set_from_stock(gtk.STOCK_EXECUTE,
            gtk.ICON_SIZE_BUTTON)
        btn_change.set_image(img_change)
        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)
        btnbox.pack_start(btn_change)
        btnbox.set_spacing(10)
        #
        self.tbl = gtk.Table (4, 3)
        self.tbl.attach(lbl_old, 0, 1, 0, 1,
            xpadding=8, ypadding=8)
        self.tbl.attach(self.ent_old, 1, 3, 0, 1,
            xpadding=8, ypadding=8)
        self.tbl.attach(lbl_new, 0, 1, 1, 2,
            xpadding=8, ypadding=8)
        self.tbl.attach(self.ent_new, 1, 3, 1, 2,
            xpadding=8, ypadding=8)
        self.tbl.attach(lbl_again, 0, 1, 2, 3,
            xpadding=8, ypadding=8)
        self.tbl.attach(self.ent_again, 1, 3, 2, 3,
            xpadding=8, ypadding=8)
        self.tbl.attach(btnbox, 0, 3, 3, 4,
            xpadding=8, ypadding=8)

        #
        self.vbox.pack_start(self.tbl, expand=False)
        return self.vbox

    def reset_ui(self):
        self.ent_old.set_text('')
        self.ent_new.set_text('')
        self.ent_again.set_text('')

    def validate_login(self, username, password):
        ret = False
        q = '''
        select password from users where user_name=?
        '''
        a = (username,)
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            try:
                mypasswd = r[1][0][0]
                if password == mypasswd:
                    ret = True
            except:
                pass
        #
        return ret

    def passwd_change(self, widget):
        ret = False
        old = self.ent_old.get_text()
        old_md5 = md5new(old).hexdigest()
        new = self.ent_new.get_text()
        new_md5 = md5new(new).hexdigest()
        again = self.ent_again.get_text()
        again_md5 = md5new(again).hexdigest()

        if self.validate_login(self.myname, old_md5):
            #correct old password
            if new_md5 == again_md5:
                if new == '':
                    msg = 'New password could not be left blank'
                    error(title='Error', message=msg, parent=self.parent)
                else:
                    #change here
                    q = '''
                    update users set password=? where id=?
                    '''
                    a = (new_md5, self.myuid)
                    r2 = db_query(q, a, self.app.database)
                    if r2[0] == 0:
                        #changed
                        msg = 'Password has been changed successfully'
                        info(title='Done', message=msg, parent=self.parent)
                        ret = True
                    else:
                        error(title='Error', message=r2[1], parent=self.parent)
            else:
                msg = 'New password mismatch'
                error(title='Error', message=msg, parent=self.parent)
        else:
            msg = 'Authentication failed'
            error(title='Error', message=msg, parent=self.parent)
        #
        if ret:
            self.reset_ui()
        #
        return ret


#----------------------------------------------------------------------#
# ui_statusbar.py                                                      #
# should provide at least: create_ui and reset_ui method               #
# create_ui() should return container                                  #
#----------------------------------------------------------------------#
class UIStatusBar:
    def __init__(self, date_format, time_format, myname, interval):
        self.version = (0, 1, 5)
        self.name = 'UI StatusBar Sample Module'
        self.info = '(c) Author, Year'
        #
        self.hbox = gtk.HBox()
        self.date_format = date_format
        self.time_format = time_format
        self.myname = myname
        self.interval = interval

    def create_ui(self):
        #stats
        self.statb_task = gtk.Statusbar()
        self.statb_task.set_has_resize_grip(False)
        #self.statb_task.get_children()[0].get_children()[0].set_alignment(0.5, 0.5)
        self.statb_task.set_size_request(-1, 25)
        self.statb_date = gtk.Statusbar()
        self.statb_date.set_has_resize_grip(False)
        #self.statb_date.get_children()[0].get_children()[0].set_alignment(0.5, 0.5)
        self.statb_date.set_size_request(-1, 25)
        self.statb_time = gtk.Statusbar()
        self.statb_time.set_has_resize_grip(False)
        #self.statb_time.get_children()[0].get_children()[0].set_alignment(0.5, 0.5)
        self.statb_time.set_size_request(-1, 25)
        self.hbox.pack_start(self.statb_task)
        self.hbox.pack_start(self.statb_date)
        self.hbox.pack_start(self.statb_time)
        #
        self.show_date_time()
        self.id_date_time = gobject.timeout_add(self.interval,
            self.show_date_time)
        self.hbox.show_all()
        return self.hbox

    def reset_ui(self):
        gobject.source_remove(self.id_date_time)

    def show_date_time(self):
        time_str = time.strftime(self.time_format)
        date_str = time.strftime(self.date_format)
        self.statb_date.push(1, date_str)
        self.statb_time.push(1, time_str)
        self.statb_task.push(1, self.myname)
        return True

    def update_task(self, info):
        self.myname = info


#----------------------------------------------------------------------#
# ui_product.py                                                        #
# should provide at least: create_ui and reset_ui method               #
# create_ui() should return container                                  #
#----------------------------------------------------------------------#
class UIProduct:
    def __init__(self, app, parent=None, myuid=0, myname=''):
        self.version = (0, 8, 9)
        self.name = 'UI Product Management Module'
        self.info = '(c) Noprianto, 2009'
        self.app = app
        self.parent = parent
        self.myuid = myuid
        self.myname = myname

        self.vbox = gtk.VBox()
        self.width = self.app.main_win_width
        self.height = self.app.main_win_height

    def create_ui(self):
        #search
        lbl_search_id = gtk.Label('ID')
        self.ent_search_id = gtk.Entry()
        self.ent_search_id.set_size_request(20, -1)
        lbl_search_pname = gtk.Label('Product name')
        self.ent_search_pname = gtk.Entry()
        self.ent_search_pname.set_size_request(40, -1)
        lbl_search_price = gtk.Label('Price (expr.)')
        btn_search_price_h = gtk.Button('?')
        btn_search_price_h.connect('clicked', self.help, 'price')
        self.ent_search_price = gtk.Entry()
        self.ent_search_price.set_size_request(40, -1)
        lbl_search_stock = gtk.Label('Stock (expr.)')
        self.ent_search_stock = gtk.Entry()
        btn_search_stock_h = gtk.Button('?')
        btn_search_stock_h.connect('clicked', self.help, 'stock')
        self.ent_search_stock.set_size_request(40, -1)
        lbl_search_cat = gtk.Label('Category')
        self.combo_search_cat = gtk.combo_box_new_text()
        self.combo_search_cat.set_size_request(40, -1)
        self.combo_search = gtk.combo_box_new_text()
        self.combo_search.append_text('OR')
        self.combo_search.append_text('AND')
        self.combo_search.set_active(0)
        btn_search_do = gtk.Button(stock=gtk.STOCK_FIND)
        btn_search_do.connect('clicked', self.product_search)
        btn_search_clear = gtk.Button(stock=gtk.STOCK_CLEAR)
        btn_search_clear.connect('clicked', self.product_search_clear)
        hb_search = gtk.HBox()
        hb_search.pack_start(lbl_search_id, padding=4,
            expand=False)
        hb_search.pack_start(self.ent_search_id, padding=4)
        hb_search.pack_start(lbl_search_pname, padding=4,
            expand=False)
        hb_search.pack_start(self.ent_search_pname, padding=4)
        hb_search.pack_start(lbl_search_price, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_price_h, expand=False)
        hb_search.pack_start(self.ent_search_price, padding=4)
        hb_search.pack_start(lbl_search_stock, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_stock_h, expand=False)
        hb_search.pack_start(self.ent_search_stock, padding=4)
        hb_search.pack_start(lbl_search_cat, padding=4,
            expand=False)
        hb_search.pack_start(self.combo_search_cat, padding=4)
        hb_search.pack_start(self.combo_search, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_do, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_clear, padding=4,
            expand=False)
        self.vbox.pack_start(hb_search, padding=10, expand=False)
        #
        #
        scrollw_main = gtk.ScrolledWindow()
        scrollw_main.set_policy(gtk.POLICY_AUTOMATIC,
            gtk.POLICY_AUTOMATIC)
        self.lstore_main = gtk.ListStore(str, str, str, str, str, str, str)
        self.trview_main = gtk.TreeView(self.lstore_main)
        self.trview_main.get_selection().set_mode(
            gtk.SELECTION_MULTIPLE)
        #
        trvcol_main_id = gtk.TreeViewColumn('ID')
        trvcol_main_id.set_min_width(80)
        cell_main_id = gtk.CellRendererText()
        trvcol_main_id.pack_start(cell_main_id, True)
        trvcol_main_id.set_attributes(cell_main_id,
            text=0)
        trvcol_main_pname = gtk.TreeViewColumn('Product Name')
        trvcol_main_pname.set_min_width(120)
        cell_main_pname = gtk.CellRendererText()
        trvcol_main_pname.pack_start(cell_main_pname, True)
        trvcol_main_pname.set_attributes(cell_main_pname,
            text=1)
        trvcol_main_cat = gtk.TreeViewColumn('Category')
        trvcol_main_cat.set_min_width(120)
        cell_main_cat = gtk.CellRendererText()
        trvcol_main_cat.pack_start(cell_main_cat, True)
        trvcol_main_cat.set_attributes(cell_main_cat,
            text=2)
        trvcol_main_price = gtk.TreeViewColumn('Price')
        trvcol_main_price.set_min_width(120)
        cell_main_price = gtk.CellRendererText()
        trvcol_main_price.pack_start(cell_main_price, True)
        trvcol_main_price.set_attributes(cell_main_price,
            text=3)
        trvcol_main_stock = gtk.TreeViewColumn('Stock')
        trvcol_main_stock.set_min_width(100)
        cell_main_stock = gtk.CellRendererText()
        trvcol_main_stock.pack_start(cell_main_stock, True)
        trvcol_main_stock.set_attributes(cell_main_stock,
            text=4)
        trvcol_main_minstock = gtk.TreeViewColumn('Min.Stock')
        trvcol_main_minstock.set_min_width(100)
        cell_main_minstock = gtk.CellRendererText()
        trvcol_main_minstock.pack_start(cell_main_minstock, True)
        trvcol_main_minstock.set_attributes(cell_main_minstock,
            text=5)
        trvcol_main_unit = gtk.TreeViewColumn('Unit')
        trvcol_main_unit.set_min_width(100)
        cell_main_unit = gtk.CellRendererText()
        trvcol_main_unit.pack_start(cell_main_unit, True)
        trvcol_main_unit.set_attributes(cell_main_unit,
            text=6)
        #
        self.trview_main.append_column(trvcol_main_id)
        self.trview_main.append_column(trvcol_main_pname)
        self.trview_main.append_column(trvcol_main_cat)
        self.trview_main.append_column(trvcol_main_price)
        self.trview_main.append_column(trvcol_main_stock)
        self.trview_main.append_column(trvcol_main_minstock)
        self.trview_main.append_column(trvcol_main_unit)
        self.trview_main.set_search_column(1)
        scrollw_main.add(self.trview_main)
        self.vbox.pack_start(scrollw_main)
        #
        self.lbl_main_count = gtk.Label()
        self.lbl_main_count.set_alignment(0.005, 0.5)
        self.vbox.pack_start(self.lbl_main_count, expand=False,
            padding=10)
        #
        #
        btn_flow = gtk.Button('C_ontrol')
        img_flow = gtk.Image()
        img_flow.set_from_stock(gtk.STOCK_EXECUTE,
            gtk.ICON_SIZE_BUTTON)
        btn_flow.set_image(img_flow)
        btn_flow.connect('clicked', self.product_flow)
        btn_viewflow = gtk.Button('_Report')
        img_viewflow = gtk.Image()
        img_viewflow.set_from_stock(gtk.STOCK_OPEN,
            gtk.ICON_SIZE_BUTTON)
        btn_viewflow.set_image(img_viewflow)
        btn_viewflow.connect('clicked', self.product_view_flow)
        btn_catedit = gtk.Button('_Category Editor')
        img_catedit = gtk.Image()
        img_catedit.set_from_stock(gtk.STOCK_EDIT,
            gtk.ICON_SIZE_BUTTON)
        btn_catedit.set_image(img_catedit)
        btn_catedit.connect('clicked', self.category_edit)
        btn_unitedit = gtk.Button('_Unit Editor')
        img_unitedit = gtk.Image()
        img_unitedit.set_from_stock(gtk.STOCK_EDIT,
            gtk.ICON_SIZE_BUTTON)
        btn_unitedit.set_image(img_unitedit)
        btn_unitedit.connect('clicked', self.unit_edit)
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.product_new)
        btn_edit = gtk.Button(stock=gtk.STOCK_EDIT)
        btn_edit.connect('clicked', self.product_edit)
        btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_del.connect('clicked', self.product_delete)
        btn_refresh = gtk.Button(stock=gtk.STOCK_REFRESH)
        btn_refresh.connect('clicked', self.product_refresh)
        btn_excsv = gtk.Button('Export CS_V')
        img_excsv = gtk.Image()
        img_excsv.set_from_stock(gtk.STOCK_SAVE,
            gtk.ICON_SIZE_BUTTON)
        btn_excsv.set_image(img_excsv)
        btn_excsv.connect('clicked', self.product_export_csv)
        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)
        btnbox.set_spacing(10)
        btnbox2 = gtk.HButtonBox()
        btnbox2.set_layout(gtk.BUTTONBOX_END)
        btnbox2.set_spacing(10)
        btnbox.pack_start(btn_flow)
        btnbox.pack_start(btn_viewflow)
        btnbox.pack_start(btn_catedit)
        btnbox.pack_start(btn_unitedit)
        btnbox2.pack_start(btn_new)
        btnbox2.pack_start(btn_edit)
        btnbox2.pack_start(btn_del)
        btnbox2.pack_start(btn_refresh)
        btnbox2.pack_start(btn_excsv)

        #
        hb_action = gtk.VBox()
        hb_btnbox = gtk.HBox()
        hb_btnbox.pack_start(btnbox, padding=10)
        hb_btnbox2 = gtk.HBox()
        hb_btnbox2.pack_start(btnbox2, padding=10)
        hb_action.pack_start(hb_btnbox, padding=10)
        hb_action.pack_start(hb_btnbox2, padding=10)
        self.vbox.pack_start(hb_action, expand=False,
            padding=10)
        #
        #tip
        self.tips = gtk.Tooltips()
        self.tips.enable()
        self.tips.set_tip(self.ent_search_stock, 'Test')

        #
        return self.vbox

    def help(self, widget, topic):
        if topic == 'price':
            helpstr = '''
            1. You can use valid SQL operator, for example:
               >, <, =, <>, >=, <=, AND, OR.
            2. Field name: price
            3. Example:
               = 1000
               > 1000
               < 1000
               > 1000 AND price < 10000

            '''
        elif topic == 'stock':
            helpstr = '''
            1. You can use valid SQL operator, for example:
               >, <, =, <>, >=, <=, AND, OR.
            2. Field name: stock
            3. Min Stock field name: minstock
            4. Example:
               = 100
               > 100
               < 100
               > 100 AND stock < 200
               = minstock
               < minstock
            '''
        else:
            helpstr = 'No help topic found'
        tips(caption='Help', tip=helpstr, width=500, parent=self.parent)

    def get_products(self, query=''):
        ret = []
        if query:
            q = query
        else:
            q = '''
            select id, product_name, price, uid, cid, stock,minstock from products order by product_name
            '''
        a = ()
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def get_product(self, id):
        ret = []
        products = self.get_products()
        for u in products:
            if u[0] == id:
                ret = u
                break
        #
        return ret


    def get_product_id(self, product):
        ret = 0
        products = self.get_products()
        for p in products:
            if p[1] == product:
                ret = p[0]
                break
        #
        return ret

    def get_product_flow(self, id):
        ret = []
        q = '''
        select dateinfo, user, pid, move_type, amount, note from moves where pid=? order by id
        '''
        a = (id,)
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret


    def get_categories(self):
        ret = []
        q = '''
        select id, category_name, note from categories order by category_name
        '''
        a = ()
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def get_category_id(self, category):
        ret = 0
        categories = self.get_categories()
        for c in categories:
            if c[1] == category:
                ret = c[0]
                break
        #
        return ret

    def get_category_name(self, cid):
        ret = ''
        categories = self.get_categories()
        for c in categories:
            if c[0] == cid:
                ret = c[1]
                break
        #
        return ret

    def get_category_note(self, category):
        ret = ''
        categories = self.get_categories()
        for c in categories:
            if c[1] == category:
                ret = c[2]
                break
        #
        return ret

    def get_category_members(self, cid):
        ret = []
        products = self.get_products()
        for p in products:
            if p[4] == cid:
                ret.append(p)
        #
        return ret

    def get_units(self):
        ret = []
        q = '''
        select id, unit_name, note from units order by unit_name
        '''
        a = ()
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def get_unit_id(self, unit):
        ret = 0
        units = self.get_units()
        for u in units:
            if u[1] == unit:
                ret = u[0]
                break
        #
        return ret

    def get_unit_name(self, uid):
        ret = ''
        units = self.get_units()
        for u in units:
            if u[0] == uid:
                ret = u[1]
                break
        #
        return ret

    def get_unit_note(self, unit):
        ret = ''
        units = self.get_units()
        for u in units:
            if u[1] == unit:
                ret = u[2]
                break
        #
        return ret

    def get_unit_members(self, uid):
        ret = []
        products = self.get_products()
        for p in products:
            if p[3] == uid:
                ret.append(p)
        #
        return ret

    def product_export_csv(self, widget):
        d = gtk.FileChooserDialog('Select output file', self.parent,
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        d.set_select_multiple(False)
        #
        filter_csv = gtk.FileFilter()
        filter_csv.set_name('CSV File')
        filter_csv.add_pattern('*.csv')
        #
        d.add_filter(filter_csv)
        #
        res = d.run()
        d.hide()
        if res == gtk.RESPONSE_OK:
            filename = d.get_filename()
            if filename:
                ent = []
                products = self.get_products()
                title = ('ID', 'Product Name', 'Category',
                    'Price', 'Stock', 'Min.Stock', 'Unit')
                ent.append(title)
                for p in products:
                    id = p[0]
                    pname = p[1]
                    price = p[2]
                    unit = self.get_unit_name(p[3])
                    cat = self.get_category_name(p[4])
                    stock = p[5]
                    minstock = p[6]
                    temp = (id, pname, cat, price, stock, minstock, unit)
                    ent.append(temp)
                #write
                try:
                    writer = csv.writer(open(filename, 'wb'))
                    writer.writerows(ent)
                    msg = 'Data have been successfully exported to %s' %(filename)
                    info(title='Done', message=msg, parent=self.parent)
                except:
                    msg = 'Failed writing to %s' %(filename)
                    error(title='Error', message=msg, parent=self.parent)
        #
        d.destroy()
        #

    def draw_products(self, query='', clear_combo=True):
        self.lstore_main.clear()
        products = self.get_products(query)
        for p in products:
            id = p[0]
            pname = p[1]
            price = p[2]
            unit = self.get_unit_name(p[3])
            cat = self.get_category_name(p[4])
            stock = p[5]
            minstock = p[6]
            temp = (id, pname, cat, price, stock, minstock, unit)
            self.lstore_main.append(temp)
        #
        msg = 'Product count: %d' %(len(products))
        self.lbl_main_count.set_text(msg)
        #
        if clear_combo:
            self.product_populate_categories(combo=self.combo_search_cat)

    def reset_ui(self):
        self.product_search_clear(widget=None)

    def product_search(self, widget):
        id = self.ent_search_id.get_text().strip()
        pname = self.ent_search_pname.get_text().strip()
        price = self.ent_search_price.get_text().strip()
        stock = self.ent_search_stock.get_text().strip()
        cat = self.combo_search_cat.get_active_text()
        cid = self.get_category_id(cat)
        rule = self.combo_search.get_active()

        #no input, quit
        if (not id) and (not pname) and (not price) and (not stock) and (not cid):
            self.product_search_clear(widget=None)
            return
        #
        rule_str = 'OR'
        if rule == 1:
            rule_str = 'AND'
        #
        id_add = ''
        if id:
            id_add = "id='%s'" %(id)
            if pname or price or stock or cid>0:
                id_add += ' %s ' %(rule_str)
        pname_add = ''
        if pname:
            pname_add = " product_name like '%%%s%%'" %(pname)
            if price or stock or cid>0:
                pname_add += ' %s ' %(rule_str)
        price_add = ''
        if price:
            price_add = " price %s " %(price)
            if stock or cid>0:
                price_add += ' %s ' %(rule_str)
        stock_add = ''
        if stock:
            stock_add = " stock %s" %(stock)
            if cid>0:
                stock_add += ' %s ' %(rule_str)
        cat_add = ''
        if cid>0:
            cat_add = ' cid=%d ' %(cid)

        query = '''
        select * from products where %s %s %s %s %s order by product_name
        ''' %(id_add, pname_add, price_add, stock_add, cat_add)


        #
        self.draw_products(query=query.strip(), clear_combo=False)
        #

    def product_search_clear(self, widget):
        self.ent_search_id.set_text('')
        self.ent_search_pname.set_text('')
        self.ent_search_price.set_text('')
        self.ent_search_stock.set_text('')
        self.combo_search_cat.set_active(0)
        self.combo_search.set_active(0)
        self.draw_products()

    def product_flow_get_idnames_model(self):
        products = self.get_products()
        idnames = [[' - '.join((x[0],x[1], '(stock: ' + str(x[5]) + ')'))] for x in products]
        #
        model = gtk.ListStore(str)
        model.append([''])#baris kosong
        for i in idnames:
            model.append(i)
        #
        return model

    def product_flow_cell_edited(self, cell, path, new_text, model, col):
        iter = model.get_iter(path)
        model.set_value(iter, col, new_text)

    def product_flow_combo_edited(self, cellrenderertext, path, new_text, trview, col):
        model = trview.get_model()
        iter = model.get_iter(path)
        model.set_value(iter, col, new_text)

    def product_flow_new_entry(self, widget, trview):
        ent = ['', '', '']
        model = trview.get_model()
        model.append(ent)

        #dapatkan baris terakhir
        iter = model.get_iter_first()
        while iter:
            lastiter = iter #simpan sebelumnya
            iter = model.iter_next(iter) #kembalikan None kalau gak ada baris terakhir
        if not iter:
            iter = lastiter
        #select
        selection = trview.get_selection()
        selection.select_iter(iter)

    def product_flow_delete_entry(self, widget, trview):
        selection = trview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            #get next row
            nextiter = model.iter_next(iter)

            #remove
            model.remove(iter)

            #select
            if nextiter:
                selection.select_iter(nextiter)

    def product_flow_save(self, widget, combo_type, cal, trview, cell_prd):
        type = combo_type.get_active_text()
        #
        date = cal.get_date()
        date2 = '%04d/%02d/%02d' %(date[0], date[1]+1, date[2])
        #
        flows = []
        model = trview.get_model()
        iter = model.get_iter_first()
        while iter:
            idname = model.get_value(iter, 0)
            id = idname.split(' - ')[0]
            amount = model.get_value(iter, 1)
            try:
                amount2 = int(amount)
            except:
                amount2 = 0
            note = model.get_value(iter, 2)
            iter = model.iter_next(iter)
            temp = (id, amount2, note)
            flows.append(temp)
        #
        q = []
        text = ''
        count = 0
        for f in flows:
            if f[0] and f[1]:
                query = '''
                insert into moves(dateinfo, user, pid, move_type, amount, note)
                values (?,?,?,?,?,?)
                '''
                args = (date2, self.myname, f[0], type, f[1], f[2])
                temp = (query, args)
                q.append(temp)
                #
                text += '[%s] %s %s %d %s\n' %(date2, f[0], type, f[1], f[2])
                count += 1
                #
                #simpan ke stock
                if type == 'IN':
                    query = '''
                    update products set stock=stock+%d where id=?
                    ''' %(f[1])
                elif type == 'OUT':
                    query = '''
                    update products set stock=stock-%d where id=?
                    ''' %(f[1])
                args = (f[0],)
                temp2 = (query, args)
                q.append(temp2)
        #
        if count:
            r = db_query_transact(q, self.app.database)
            if r[0] == 0:
                msg = 'All transactions have been saved successfully\n\n%s' %(text)
                info(parent=self.parent, title='Done', message=msg)
                model.clear()
                #combo dibuat ulang dengan data terbaru
                cell_prd.set_property('model', self.product_flow_get_idnames_model())
                #
                #draw ulang produk
                self.draw_products()
            else:
                error(parent=self.parent, title='Error', message=r[1])

    def product_view_flow(self, widget):
        selection = self.trview_main.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            iter = iters[0]
            id = model.get_value(iter, 0)
            #
            product = self.get_product(id)
            pname = product[1]
            stock = product[5]
            pinfo = '<b>Product</b>: %s - %s, <b>Stock</b>: %d' %(id, pname, stock)
            lbl_info = gtk.Label()
            lbl_info.set_alignment(0.01, 0.5)
            lbl_info.set_markup(pinfo)
            #
            lstore = gtk.ListStore(str, str, str, str, str)
            trview = gtk.TreeView(lstore)
            scrollw = gtk.ScrolledWindow()
            scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            scrollw.add(trview)
            trvcol_date = gtk.TreeViewColumn('Date')
            trvcol_date.set_min_width(120)
            trvcol_user = gtk.TreeViewColumn('User')
            trvcol_user.set_min_width(120)
            trvcol_flow = gtk.TreeViewColumn('Type')
            trvcol_flow.set_min_width(120)
            trvcol_amt = gtk.TreeViewColumn('Amount')
            trvcol_amt.set_min_width(120)
            trvcol_note = gtk.TreeViewColumn('Note')
            trvcol_note.set_min_width(120)
            cell_user = gtk.CellRendererText()
            cell_date = gtk.CellRendererText()
            cell_flow = gtk.CellRendererText()
            cell_amt = gtk.CellRendererText()
            cell_note = gtk.CellRendererText()
            trvcol_date.pack_start(cell_date, True)
            trvcol_date.set_attributes(cell_date, text=0)
            trvcol_user.pack_start(cell_user, True)
            trvcol_user.set_attributes(cell_user, text=1)
            trvcol_flow.pack_start(cell_flow, True)
            trvcol_flow.set_attributes(cell_flow, text=2)
            trvcol_amt.pack_start(cell_amt, True)
            trvcol_amt.set_attributes(cell_amt, text=3)
            trvcol_note.pack_start(cell_note, True)
            trvcol_note.set_attributes(cell_note, text=4)
            trview.append_column(trvcol_date)
            trview.append_column(trvcol_user)
            trview.append_column(trvcol_flow)
            trview.append_column(trvcol_amt)
            trview.append_column(trvcol_note)
            #
            flows = self.get_product_flow(id)
            lstore.clear()
            for f in flows:
                dateinfo = f[0]
                user = f[1]
                flow_type = f[3]
                amount = f[4]
                note = f[5]
                ent = [dateinfo, user, flow_type, amount, note]
                lstore.append(ent)
            #
            d = gtk.Dialog('Report',
                self.parent, gtk.DIALOG_MODAL,
                (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
            d.set_size_request(
                self.width - 100, self.height - 50)
            #
            d.vbox.pack_start(lbl_info, expand=False, padding=10)
            d.vbox.pack_start(scrollw, expand=True, padding=10)
            #
            d.vbox.show_all()
            #
            ret = d.run()
            d.destroy()
            #


    def product_flow(self, widget):
        self.product_flow_dialog = gtk.Dialog('Control',
            self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.product_flow_dialog.set_size_request(
            self.width - 100, self.height - 50)
        #
        combo_type = gtk.combo_box_new_text()
        combo_type.append_text('IN')
        combo_type.append_text('OUT')
        combo_type.set_active(0)
        #
        cal = gtk.Calendar()
        bgcolor = gtk.gdk.Color(250*255, 255*255, 210*255)
        #
        lstore = gtk.ListStore(str, str, str)
        trview = gtk.TreeView(lstore)
        trvcol_prd = gtk.TreeViewColumn('Product')
        trvcol_prd.set_min_width(300)
        cell_prd = gtk.CellRendererCombo()
        cell_prd.set_property('text-column', 0)
        cell_prd.set_property('editable', True)
        cell_prd.set_property('has-entry', False)
        cell_prd.set_property('model', self.product_flow_get_idnames_model())
        cell_prd.set_property('cell-background-gdk', bgcolor)
        cell_prd.connect('edited', self.product_flow_combo_edited, trview, 0)
        trvcol_prd.pack_start(cell_prd, True)
        trvcol_prd.set_attributes(cell_prd, text=0)
        trvcol_amt = gtk.TreeViewColumn('Amount')
        trvcol_amt.set_min_width(120)
        cell_amt = gtk.CellRendererText()
        cell_amt.set_property('editable', True)
        cell_amt.set_property('cell-background-gdk', bgcolor)
        cell_amt.connect('edited', self.product_flow_cell_edited, lstore, 1)
        trvcol_amt.pack_start(cell_amt, True)
        trvcol_amt.set_attributes(cell_amt, text=1)
        trvcol_note = gtk.TreeViewColumn('Note')
        trvcol_note.set_min_width(120)
        cell_note = gtk.CellRendererText()
        cell_note.set_property('editable', True)
        cell_note.set_property('cell-background-gdk', bgcolor)
        cell_note.connect('edited', self.product_flow_cell_edited, lstore, 2)
        trvcol_note.pack_start(cell_note, True)
        trvcol_note.set_attributes(cell_note, text=2)
        trview.append_column(trvcol_prd)
        trview.append_column(trvcol_amt)
        trview.append_column(trvcol_note)
        #
        scrollw = gtk.ScrolledWindow()
        scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollw.add(trview)
        #
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.product_flow_new_entry, trview)
        btn_delete = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_delete.connect('clicked', self.product_flow_delete_entry, trview)
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_save.connect('clicked', self.product_flow_save, combo_type, cal, trview, cell_prd)
        btnbox = gtk.HButtonBox()
        btnbox.set_spacing(10)
        btnbox.set_layout(gtk.BUTTONBOX_END)
        btnbox.pack_start(btn_new)
        btnbox.pack_start(btn_delete)
        btnbox.pack_start(btn_save)
        #
        self.product_flow_dialog.vbox.pack_start(combo_type, expand=False,
            padding=4)
        self.product_flow_dialog.vbox.pack_start(cal, expand=False,
            padding=4)
        self.product_flow_dialog.vbox.pack_start(scrollw, expand=True,
            padding=4)
        self.product_flow_dialog.vbox.pack_start(btnbox, expand=False,
            padding=4)
        self.product_flow_dialog.vbox.show_all()
        #
        ret = self.product_flow_dialog.run()
        self.product_flow_dialog.destroy()
        #
        return ret


    def product_new(self, widget):
        d = gtk.Dialog('New Product', self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        d.set_size_request(self.app.main_win_width - 100, -1)

        tbl_prd = gtk.Table(6, 3)
        #
        ent_id = gtk.Entry()
        lbl_id = gtk.Label('Product ID')
        lbl_id.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_id, 0, 1, 0, 1, xpadding=8, ypadding=8)
        tbl_prd.attach(ent_id, 1, 3, 0, 1, xpadding=8, ypadding=8)
        #
        ent_pname = gtk.Entry()
        lbl_pname = gtk.Label('Product Name')
        lbl_pname.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_pname, 0, 1, 1, 2, xpadding=8, ypadding=8)
        tbl_prd.attach(ent_pname, 1, 3, 1, 2, xpadding=8, ypadding=8)
        #
        ent_price = gtk.Entry()
        lbl_price = gtk.Label('Price')
        lbl_price.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_price, 0, 1, 2, 3, xpadding=8, ypadding=8)
        tbl_prd.attach(ent_price, 1, 3, 2, 3, xpadding=8, ypadding=8)
        #
        combo_unit = gtk.combo_box_new_text()
        self.product_populate_units(combo=combo_unit)
        lbl_unit = gtk.Label('Unit')
        lbl_unit.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_unit, 0, 1, 3, 4, xpadding=8, ypadding=8)
        tbl_prd.attach(combo_unit, 1, 3, 3, 4, xpadding=8, ypadding=8)
        #
        combo_cat = gtk.combo_box_new_text()
        self.product_populate_categories(combo=combo_cat)
        lbl_cat = gtk.Label('Category')
        lbl_cat.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_cat, 0, 1, 4, 5, xpadding=8, ypadding=8)
        tbl_prd.attach(combo_cat, 1, 3, 4, 5, xpadding=8, ypadding=8)
        #
        ent_minstock = gtk.Entry()
        lbl_minstock = gtk.Label('Min Stock')
        lbl_minstock.set_alignment(0, 0.5)
        tbl_prd.attach(lbl_minstock, 0, 1, 5, 6, xpadding=8, ypadding=8)
        tbl_prd.attach(ent_minstock, 1, 3, 5, 6, xpadding=8, ypadding=8)
        #

        d.vbox.pack_start(tbl_prd)
        d.vbox.show_all()
        #
        ret = d.run()
        d.hide()

        if ret == gtk.RESPONSE_ACCEPT:
            pid = ent_id.get_text().strip()
            pname = ent_pname.get_text().strip()
            price = ent_price.get_text().strip()
            try:
                price2 = float(price)
            except:
                price2 = 0
            unit = combo_unit.get_active_text()
            uid = 0
            if unit:
                uid = self.get_unit_id(unit)
            cat = combo_cat.get_active_text()
            cid = 0
            if cat:
                cid = self.get_category_id(cat)
            minstock = ent_minstock.get_text().strip()
            try:
                minstock2 = int(minstock)
            except:
                minstock2 = 0


            if not pid or not pname:
                msg = 'ID and Product Name cannot be left blank'
                error(parent=self.parent, message=msg,
                    title='Error')
            else:
                found = self.get_product(pid)
                if found:
                    msg = 'Product %s already exists' %(pid)
                    error(message=msg, parent=d, title='Error')
                else:
                    q = '''
                    insert into products(id, product_name, price, uid, cid, stock,minstock)
                    values(?,?,?,?,?,?,?)
                    '''
                    a = (pid, pname, price2, uid, cid, 0, minstock2)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=d)
                    #
                    self.draw_products()
        #
        d.destroy()

    def product_edit(self, widget):
        selection = self.trview_main.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            iter = iters[0]
            id = model.get_value(iter, 0)
            product = self.get_product(id)
            #
            d = gtk.Dialog('Edit Product', self.parent, gtk.DIALOG_MODAL,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            d.set_size_request(self.app.main_win_width - 100, -1)

            tbl_prd = gtk.Table(5, 3)
            #
            lbl_id2 = gtk.Label(id)
            lbl_id2.set_alignment(0, 0.5)
            lbl_id = gtk.Label('Product ID')
            lbl_id.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_id, 0, 1, 0, 1, xpadding=8, ypadding=8)
            tbl_prd.attach(lbl_id2, 1, 3, 0, 1, xpadding=8, ypadding=8)
            #
            ent_pname = gtk.Entry()
            ent_pname.set_text(product[1])
            lbl_pname = gtk.Label('Product Name')
            lbl_pname.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_pname, 0, 1, 1, 2, xpadding=8, ypadding=8)
            tbl_prd.attach(ent_pname, 1, 3, 1, 2, xpadding=8, ypadding=8)
            #
            ent_price = gtk.Entry()
            ent_price.set_text(str(product[2]))
            lbl_price = gtk.Label('Price')
            lbl_price.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_price, 0, 1, 2, 3, xpadding=8, ypadding=8)
            tbl_prd.attach(ent_price, 1, 3, 2, 3, xpadding=8, ypadding=8)
            #
            combo_unit = gtk.combo_box_new_text()
            uid = product[3]
            unit = self.get_unit_name(uid)
            self.product_populate_units(combo=combo_unit, active=unit)
            lbl_unit = gtk.Label('Unit')
            lbl_unit.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_unit, 0, 1, 3, 4, xpadding=8, ypadding=8)
            tbl_prd.attach(combo_unit, 1, 3, 3, 4, xpadding=8, ypadding=8)
            #
            combo_cat = gtk.combo_box_new_text()
            cid = product[4]
            cat = self.get_category_name(cid)
            self.product_populate_categories(combo=combo_cat, active=cat)
            lbl_cat = gtk.Label('Category')
            lbl_cat.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_cat, 0, 1, 4, 5, xpadding=8, ypadding=8)
            tbl_prd.attach(combo_cat, 1, 3, 4, 5, xpadding=8, ypadding=8)
            #
            ent_minstock = gtk.Entry()
            ent_minstock.set_text(str(product[6]))
            lbl_minstock = gtk.Label('Min Stock')
            lbl_minstock.set_alignment(0, 0.5)
            tbl_prd.attach(lbl_minstock, 0, 1, 5, 6, xpadding=8, ypadding=8)
            tbl_prd.attach(ent_minstock, 1, 3, 5, 6, xpadding=8, ypadding=8)

            #
            d.vbox.pack_start(tbl_prd)
            d.vbox.show_all()
            #
            ret = d.run()
            d.hide()

            if ret == gtk.RESPONSE_ACCEPT:
                pname = ent_pname.get_text().strip()
                price = ent_price.get_text().strip()
                try:
                    price2 = float(price)
                except:
                    price2 = 0
                unit = combo_unit.get_active_text()
                uid = 0
                if unit:
                    uid = self.get_unit_id(unit)
                cat = combo_cat.get_active_text()
                cid = 0
                if cat:
                    cid = self.get_category_id(cat)
                minstock = ent_minstock.get_text().strip()
                try:
                    minstock2 = int(minstock)
                except:
                    minstock2 = 0

                if not pname:
                    msg = 'Product Name could not be left blank'
                    error(parent=self.parent, message=msg,
                        title='Error')
                else:
                    q = '''
                    update products set product_name=?, price=?, uid=?, cid=?, minstock=?
                    where id=?
                    '''
                    a = (pname, price2, uid, cid, minstock2, id)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=d)
                    #
                    self.draw_products()
            #
            d.destroy()


    def product_delete(self, widget):
        selection = self.trview_main.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            ids = [model.get_value(iter, 0) for iter in iters]
            names = [model.get_value(iter, 1) for iter in iters]

            count = len(ids)
            info_delete_str = '\n'.join(names)
            #
            if count > 0:
                msg = 'Are you sure you want to '
                msg += 'delete %d product(s)?' %(count)
                msg2 = 'Selected product(s):\n' + info_delete_str
                msg2 += '\n\nAll corresponding data will also be deleted.'
                msg2 += '\nThis action can not be undone.'

                ok = confirm(title='Please confirm',
                    message=msg, message2=msg2, parent=self.parent,
                    buttons=gtk.BUTTONS_YES_NO)

                #if yes,
                if ok == gtk.RESPONSE_YES:
                    q = []
                    for id in ids:
                        query = 'delete from products where id=?'
                        args = (id,)
                        temp = (query, args)
                        q.append(temp)
                    r = db_query_transact(q, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=self.parent)
                    #
                    self.draw_products()


    def product_refresh(self, widget):
        self.draw_products()

    def product_populate_categories(self, combo, active=''):
        categories = self.get_categories()
        category_name = [x[1] for x in categories]
        #
        model = combo.get_model()
        model.clear()
        #
        combo.append_text('')
        i = 1
        activeindex = 0
        for c in category_name:
            combo.append_text(c)
            if c == active:
                activeindex = i
            i += 1
        if active:
            combo.set_active(activeindex)
        else:
            combo.set_active(0)

    def product_populate_units(self, combo, active=''):
        units = self.get_units()
        units_name = [x[1] for x in units]
        #
        model = combo.get_model()
        model.clear()
        #
        combo.append_text('')
        i = 1
        activeindex = 0
        for u in units_name:
            combo.append_text(u)
            if u == active:
                activeindex = i
            i += 1
        if active:
            combo.set_active(activeindex)
        else:
            combo.set_active(0)

    def category_rename(self, widget):
        category = self.combo_cat.get_active_text()
        if category:
            newcat = input(title='Rename Category', label='New category name',
            parent=self.cat_edit_dialog, default=category).strip().upper()
            if newcat and newcat != category:
                categories = self.get_categories()
                found=self.get_category_id(newcat)
                if found:
                    msg = 'Category %s already exists' %(newcat)
                    error(title='Error', message=msg,
                        parent=self.parent)
                else:
                    q = '''
                    update categories set category_name=? where category_name=?
                    '''
                    a = (newcat, category)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=self.cat_edit_dialog)
                    else:
                        self.product_populate_categories(combo=self.combo_cat, active=newcat)


    def category_new(self, widget):
        category = input(title='New Category', label='Category name',
            parent=self.cat_edit_dialog).strip().upper()
        if category:
            categories = self.get_categories()
            found=self.get_category_id(category)
            #
            if found:
                msg = 'Category %s already exists' %(category)
                error(title='Error', message=msg,
                    parent=self.parent)
            else:
                q = '''
                insert into categories(category_name, note)
                values(?,?)
                '''
                a = (category,'')
                r = db_query(q, a, self.app.database)
                if r[0] != 0:
                    msg = r[1]
                    dialog = error
                    dialog(title='Error', message=msg, parent=self.cat_edit_dialog)
                else:
                    self.product_populate_categories(active=category, combo=self.combo_cat)


    def category_delete(self, widget):
        category = self.combo_cat.get_active_text()
        if category:
            cid = self.get_category_id(category)
            members = self.get_category_members(cid)
            members_count = len(members)
            if members_count:
                msg = '''Category has %d member(s).\nAre you sure you want to delete category %s?\nAll products in this category will lose it's category information.''' %(
                members_count, category)
            else:
                msg = '''Are you sure you want to delete category %s?''' %(category)
            #
            ok = confirm(title='Please confirm', message=msg,
                parent=self.cat_edit_dialog, buttons=gtk.BUTTONS_YES_NO)
            if ok == gtk.RESPONSE_YES:
                q1 = '''
                update products set cid=0 where cid=?
                '''
                a1 = (cid,)
                q2 = '''
                delete from categories where id=?
                '''
                a2 = (cid,)
                q = ((q1, a1), (q2, a2))
                r = db_query_transact(q, self.app.database)
                if r[0] == 0:
                    msg = 'Category %s has been deleted successfully' %(category)
                    dialog = info
                else:
                    msg = r[1]
                    dialog = error
                dialog(title='Result', message=msg, parent=self.cat_edit_dialog)
                #
                self.product_populate_categories(combo=self.combo_cat)
                self.combo_cat.popup()


    def category_save(self, widget):
        category = self.combo_cat.get_active_text()
        if category:
            cid = self.get_category_id(category)
            model = self.cat_propedit.model
            iter = model.get_iter_first()
            note = model.get_value(iter, 1)
            #
            q = '''
            update categories set note=? where id=?
            '''
            a = (note, cid)
            r = db_query(q, a, self.app.database)
            if r[0] == 0:
                msg = 'Settings for category %s have been saved successfully' %(category)
                dialog = info
            else:
                msg = r[1]
                dialog = error
            dialog(title='Result', message=msg, parent=self.cat_edit_dialog)
            #


    def category_get_prop(self, combo):
        category = combo.get_active_text()
        if category:
            self.cat_propedit.clear()
            note = self.get_category_note(category)
            cid = self.get_category_id(category)
            data = (('Note', note),)
            self.cat_propedit.fill(data)
            members = self.get_category_members(cid)
            members_info = 'Member count: %d' %(len(members))
        else:
            self.cat_propedit.clear()
            members_info = ''
        self.lbl_cat_members.set_text(members_info)


    def category_edit(self, widget):
        self.cat_edit_dialog = gtk.Dialog('Category Editor',
            self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.cat_edit_dialog.set_size_request(
            self.width - 100, self.height - 100)
        #
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        #
        self.combo_cat = gtk.combo_box_new_text()
        self.product_populate_categories(combo=self.combo_cat)
        #
        self.cat_propedit = SimplePropertyEditor()
        #
        vbox.pack_start(self.combo_cat, padding=4, expand=False)
        vbox.pack_start(self.cat_propedit.scrolledwin, padding=4)
        #
        btnbox = gtk.VButtonBox()
        btnbox.set_spacing(10)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_save.get_children()[0].get_children()[0].get_children()[1].set_text('Save settings')
        btn_save.connect('clicked', self.category_save)
        btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_del.connect('clicked', self.category_delete)
        btn_rename = gtk.Button(stock=gtk.STOCK_EDIT)
        btn_rename.get_children()[0].get_children()[0].get_children()[1].set_text('Rename')
        btn_rename.connect('clicked', self.category_rename)
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.category_new)
        btnbox.pack_start(btn_save)
        btnbox.pack_start(btn_rename)
        btnbox.pack_start(btn_del)
        btnbox.pack_start(btn_new)
        #
        self.lbl_cat_members = gtk.Label()
        self.lbl_cat_members.set_alignment(0.02, 0.5)
        #
        hbox.pack_start(vbox, padding=8)
        hbox.pack_start(btnbox, expand=False, padding=8)
        #
        self.combo_cat.connect('changed', self.category_get_prop)
        #
        self.cat_edit_dialog.vbox.pack_start(hbox, padding=4)
        self.cat_edit_dialog.vbox.pack_start(self.lbl_cat_members, padding=4,
            expand=False)
        self.cat_edit_dialog.vbox.show_all()
        #
        ret = self.cat_edit_dialog.run()
        self.cat_edit_dialog.destroy()
        #
        self.draw_products()
        return ret


    def unit_rename(self, widget):
        unit = self.combo_unit.get_active_text()
        if unit:
            newunit = input(title='Rename Unit', label='New unit name',
            parent=self.unit_edit_dialog, default=unit).strip().upper()
            if newunit and newunit != unit:
                found=self.get_unit_id(newunit)
                if found:
                    msg = 'Unit %s already exists' %(newunit)
                    error(title='Error', message=msg,
                        parent=self.parent)
                else:
                    q = '''
                    update units set unit_name=? where unit_name=?
                    '''
                    a = (newunit, unit)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=self.unit_edit_dialog)
                    else:
                        self.product_populate_units(combo=self.combo_unit, active=newunit)


    def unit_new(self, widget):
        unit = input(title='New Unit', label='Unit name',
            parent=self.unit_edit_dialog).strip().upper()
        if unit:
            found=self.get_unit_id(unit)
            #
            if found:
                msg = 'Unit %s already exists' %(unit)
                error(title='Error', message=msg,
                    parent=self.parent)
            else:
                q = '''
                insert into units(unit_name, note)
                values(?,?)
                '''
                a = (unit,'')
                r = db_query(q, a, self.app.database)
                if r[0] != 0:
                    msg = r[1]
                    dialog = error
                    dialog(title='Error', message=msg, parent=self.unit_edit_dialog)
                else:
                    self.product_populate_units(active=unit, combo=self.combo_unit)

    def unit_delete(self, widget):
        unit = self.combo_unit.get_active_text()
        if unit:
            uid = self.get_unit_id(unit)
            members = self.get_unit_members(uid)
            members_count = len(members)
            if members_count:
                msg = '''Unit has %d member(s).\nAre you sure you want to delete unit %s?\nAll products in this unit will lose it's unit information.''' %(
                members_count, unit)
            else:
                msg = '''Are you sure you want to delete unit %s?''' %(unit)
            #
            ok = confirm(title='Please confirm', message=msg,
                parent=self.unit_edit_dialog, buttons=gtk.BUTTONS_YES_NO)
            if ok == gtk.RESPONSE_YES:
                q1 = '''
                update products set uid=0 where uid=?
                '''
                a1 = (uid,)
                q2 = '''
                delete from units where id=?
                '''
                a2 = (uid,)
                q = ((q1, a1), (q2, a2))
                r = db_query_transact(q, self.app.database)
                if r[0] == 0:
                    msg = 'Unit %s has been deleted successfully' %(unit)
                    dialog = info
                else:
                    msg = r[1]
                    dialog = error
                dialog(title='Result', message=msg, parent=self.unit_edit_dialog)
                #
                self.product_populate_units(combo=self.combo_unit)
                self.combo_unit.popup()

    def unit_save(self, widget):
        unit = self.combo_unit.get_active_text()
        if unit:
            uid = self.get_unit_id(unit)
            model = self.unit_propedit.model
            iter = model.get_iter_first()
            note = model.get_value(iter, 1)
            #
            q = '''
            update units set note=? where id=?
            '''
            a = (note, uid)
            r = db_query(q, a, self.app.database)
            if r[0] == 0:
                msg = 'Settings for unit %s have been saved successfully' %(unit)
                dialog = info
            else:
                msg = r[1]
                dialog = error
            dialog(title='Result', message=msg, parent=self.unit_edit_dialog)
            #

    def unit_get_prop(self, combo):
        unit = combo.get_active_text()
        if unit:
            self.unit_propedit.clear()
            note = self.get_unit_note(unit)
            uid = self.get_unit_id(unit)
            data = (('Note', note),)
            self.unit_propedit.fill(data)
            members = self.get_unit_members(uid)
            members_info = 'Member count: %d' %(len(members))
        else:
            self.unit_propedit.clear()
            members_info = ''
        self.lbl_unit_members.set_text(members_info)


    def unit_edit(self, widget):
        self.unit_edit_dialog = gtk.Dialog('Unit Editor',
            self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.unit_edit_dialog.set_size_request(
            self.width - 100, self.height - 100)
        #
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        #
        self.combo_unit = gtk.combo_box_new_text()
        self.product_populate_units(combo=self.combo_unit)
        #
        self.unit_propedit = SimplePropertyEditor()
        #
        vbox.pack_start(self.combo_unit, padding=4, expand=False)
        vbox.pack_start(self.unit_propedit.scrolledwin, padding=4)
        #
        btnbox = gtk.VButtonBox()
        btnbox.set_spacing(10)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_save.get_children()[0].get_children()[0].get_children()[1].set_text('Save settings')
        btn_save.connect('clicked', self.unit_save)
        btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_del.connect('clicked', self.unit_delete)
        btn_rename = gtk.Button(stock=gtk.STOCK_EDIT)
        btn_rename.get_children()[0].get_children()[0].get_children()[1].set_text('Rename')
        btn_rename.connect('clicked', self.unit_rename)
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.unit_new)
        btnbox.pack_start(btn_save)
        btnbox.pack_start(btn_rename)
        btnbox.pack_start(btn_del)
        btnbox.pack_start(btn_new)
        #
        self.lbl_unit_members = gtk.Label()
        self.lbl_unit_members.set_alignment(0.02, 0.5)
        #
        hbox.pack_start(vbox, padding=8)
        hbox.pack_start(btnbox, expand=False, padding=8)
        #
        self.combo_unit.connect('changed', self.unit_get_prop)
        #
        self.unit_edit_dialog.vbox.pack_start(hbox, padding=4)
        self.unit_edit_dialog.vbox.pack_start(self.lbl_unit_members, padding=4,
            expand=False)
        self.unit_edit_dialog.vbox.show_all()
        #
        ret = self.unit_edit_dialog.run()
        self.unit_edit_dialog.destroy()
        #
        self.draw_products()
        return ret


#----------------------------------------------------------------------#
# ui_user.py                                                           #
# should provide at least: create_ui and reset_ui method               #
# create_ui() should return container                                  #
#----------------------------------------------------------------------#
class UIUser:
    def __init__(self, app, parent=None, myuid=0, myname='',
        external_func_user_edit=None):
        self.version = (0, 7, 8)
        self.name = 'UI User Management Module'
        self.info = '(c) Noprianto, 2009'
        self.app = app
        self.parent = parent
        self.myuid = myuid
        self.myname = myname
        self.external_func_user_edit = external_func_user_edit

        self.vbox = gtk.VBox()
        self.width = self.app.main_win_width
        self.height = self.app.main_win_height

    def create_ui(self):
        #search
        lbl_search_uname = gtk.Label('User name')
        self.ent_search_uname = gtk.Entry()
        lbl_search_rname = gtk.Label('Real name')
        self.ent_search_rname = gtk.Entry()
        self.combo_search = gtk.combo_box_new_text()
        self.combo_search.append_text('OR')
        self.combo_search.append_text('AND')
        self.combo_search.set_active(0)
        btn_search_do = gtk.Button(stock=gtk.STOCK_FIND)
        btn_search_do.connect('clicked', self.user_search)
        btn_search_clear = gtk.Button(stock=gtk.STOCK_CLEAR)
        btn_search_clear.connect('clicked', self.user_search_clear)
        hb_search = gtk.HBox()
        hb_search.pack_start(lbl_search_uname, padding=4,
            expand=False)
        hb_search.pack_start(self.ent_search_uname, padding=4)
        hb_search.pack_start(lbl_search_rname, padding=4,
            expand=False)
        hb_search.pack_start(self.ent_search_rname, padding=4)
        hb_search.pack_start(self.combo_search, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_do, padding=4,
            expand=False)
        hb_search.pack_start(btn_search_clear, padding=4,
            expand=False)
        self.vbox.pack_start(hb_search, padding=10, expand=False)
        #
        #
        scrollw_main = gtk.ScrolledWindow()
        scrollw_main.set_policy(gtk.POLICY_AUTOMATIC,
            gtk.POLICY_AUTOMATIC)
        self.lstore_main = gtk.ListStore(str, str, str, str)
        self.trview_main = gtk.TreeView(self.lstore_main)
        self.trview_main.get_selection().set_mode(
            gtk.SELECTION_MULTIPLE)
        #
        trvcol_main_id = gtk.TreeViewColumn('ID')
        trvcol_main_id.set_min_width(80)
        cell_main_id = gtk.CellRendererText()
        trvcol_main_id.pack_start(cell_main_id, True)
        trvcol_main_id.set_attributes(cell_main_id,
            text=0)
        trvcol_main_uname = gtk.TreeViewColumn('User Name')
        trvcol_main_uname.set_min_width(140)
        cell_main_uname = gtk.CellRendererText()
        trvcol_main_uname.pack_start(cell_main_uname, True)
        trvcol_main_uname.set_attributes(cell_main_uname,
            text=1)
        trvcol_main_rname = gtk.TreeViewColumn('Real Name')
        trvcol_main_rname.set_min_width(240)
        cell_main_rname = gtk.CellRendererText()
        trvcol_main_rname.pack_start(cell_main_rname, True)
        trvcol_main_rname.set_attributes(cell_main_rname,
            text=2)
        trvcol_main_group = gtk.TreeViewColumn('Group')
        trvcol_main_group.set_min_width(140)
        cell_main_group = gtk.CellRendererText()
        trvcol_main_group.pack_start(cell_main_group, True)
        trvcol_main_group.set_attributes(cell_main_group,
            text=3)
        #
        self.trview_main.append_column(trvcol_main_id)
        self.trview_main.append_column(trvcol_main_uname)
        self.trview_main.append_column(trvcol_main_rname)
        self.trview_main.append_column(trvcol_main_group)
        self.trview_main.set_search_column(1)
        scrollw_main.add(self.trview_main)
        self.vbox.pack_start(scrollw_main)
        #
        self.lbl_main_count = gtk.Label()
        self.lbl_main_count.set_alignment(0.005, 0.5)
        self.vbox.pack_start(self.lbl_main_count, expand=False,
            padding=10)
        #
        #
        btn_groupedit = gtk.Button('_Group Editor')
        img_groupedit = gtk.Image()
        img_groupedit.set_from_stock(gtk.STOCK_EDIT,
            gtk.ICON_SIZE_BUTTON)
        btn_groupedit.set_image(img_groupedit)
        btn_groupedit.connect('clicked', self.group_edit)
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.user_new)
        btn_edit = gtk.Button(stock=gtk.STOCK_EDIT)
        btn_edit.connect('clicked', self.user_edit)
        btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_del.connect('clicked', self.user_delete)
        btn_refresh = gtk.Button(stock=gtk.STOCK_REFRESH)
        btn_refresh.connect('clicked', self.user_refresh)
        btnbox = gtk.HButtonBox()
        btnbox.set_layout(gtk.BUTTONBOX_END)
        btnbox.pack_start(btn_groupedit)
        btnbox.pack_start(btn_new)
        btnbox.pack_start(btn_edit)
        btnbox.pack_start(btn_del)
        btnbox.pack_start(btn_refresh)
        btnbox.set_spacing(10)
        #
        hb_action = gtk.HBox()
        hb_action.pack_start(btnbox, padding=10)
        self.vbox.pack_start(hb_action, expand=False,
            padding=10)
        #
        return self.vbox

    def get_users(self, query=''):
        ret = []
        if query:
            q = query
        else:
            q = '''
            select id, user_name, real_name, gid, password from users order by user_name
            '''
        a = ()
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def get_user(self, id):
        ret = []
        users = self.get_users()
        for u in users:
            if u[0] == id:
                ret = u
                break
        #
        return ret


    def get_user_id(self, user):
        ret = 0
        users = self.get_users()
        for u in users:
            if u[1] == user:
                ret = u[0]
                break
        #
        return ret

    def get_user_group(self, user):
        ret = 0
        users = self.get_users()
        for u in users:
            if u[1] == user:
                ret = u[3]
                break
        #
        return ret

    def get_group_resources(self, group):
        ret = []
        q = '''
        select resources from groups where group_name=?
        '''
        a = (group,)
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            try:
                res = r[1][0][0]
                if res:
                    ret = res.split(',')
                    ret.sort()
            except:
                ret = []
        return ret

    def get_groups(self):
        ret = []
        q = '''
        select id, group_name, resources from groups order by group_name
        '''
        a = ()
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def get_group_id(self, group):
        ret = 0
        groups = self.get_groups()
        for g in groups:
            if g[1] == group:
                ret = g[0]
                break
        #
        return ret

    def get_group_name(self, gid):
        ret = ''
        groups = self.get_groups()
        for g in groups:
            if g[0] == gid:
                ret = g[1]
                break
        #
        return ret

    def get_group_members(self, group):
        ret = []
        gid = self.get_group_id(group)
        q = '''
        select * from users where gid=? order by user_name
        '''
        a = (gid,)
        r = db_query(q, a, self.app.database)
        if r[0] == 0:
            ret = r[1]
        return ret

    def draw_users(self, query=''):
        self.lstore_main.clear()
        users = self.get_users(query)
        for u in users:
            id = u[0]
            uname = u[1]
            rname = u[2]
            gid = u[3]
            group = self.get_group_name(gid)
            temp = (id, uname, rname, group)
            self.lstore_main.append(temp)
        #
        msg = 'User count: %d' %(len(users))
        self.lbl_main_count.set_text(msg)

    def reset_ui(self):
        self.user_search_clear(widget=None)

    def user_search(self, widget):
        uname = self.ent_search_uname.get_text().strip()
        rname = self.ent_search_rname.get_text().strip()
        rule = self.combo_search.get_active()

        #no input, quit
        if not uname and not rname:
            self.user_search_clear(widget=None)
            return
        #
        rule_str = 'OR'
        if rule == 1:
            rule_str = 'AND'
        #
        uname_add = ''
        if uname:
            uname_add = "user_name like '%%%s%%'" %(uname)
            if rname:
                uname_add += ' %s ' %(rule_str)
        rname_add = ''
        if rname:
            rname_add = "real_name like '%%%s%%'" %(rname)

        query = '''
        select * from users where %s %s order by user_name
        ''' %(uname_add, rname_add)

        #
        self.draw_users(query=query.strip())
        #

    def user_search_clear(self, widget):
        self.ent_search_uname.set_text('')
        self.ent_search_rname.set_text('')
        self.combo_search.set_active(0)
        self.draw_users()

    def user_new(self, widget):
        d = gtk.Dialog('New User', self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        d.set_size_request(self.app.main_win_width - 100, -1)

        tbl_user = gtk.Table(4, 3)
        #
        ent_uname = gtk.Entry()
        lbl_uname = gtk.Label('User Name')
        lbl_uname.set_alignment(0, 0.5)
        tbl_user.attach(lbl_uname, 0, 1, 0, 1, xpadding=8, ypadding=8)
        tbl_user.attach(ent_uname, 1, 3, 0, 1, xpadding=8, ypadding=8)
        #
        ent_rname = gtk.Entry()
        lbl_rname = gtk.Label('Real Name')
        lbl_rname.set_alignment(0, 0.5)
        tbl_user.attach(lbl_rname, 0, 1, 1, 2, xpadding=8, ypadding=8)
        tbl_user.attach(ent_rname, 1, 3, 1, 2, xpadding=8, ypadding=8)
        #
        ent_passwd = gtk.Entry()
        lbl_passwd = gtk.Label('Password')
        lbl_passwd.set_alignment(0, 0.5)
        tbl_user.attach(lbl_passwd, 0, 1, 2, 3, xpadding=8, ypadding=8)
        tbl_user.attach(ent_passwd, 1, 3, 2, 3, xpadding=8, ypadding=8)
        #
        combo_group = gtk.combo_box_new_text()
        self.group_populate_groups(combo=combo_group)
        lbl_group = gtk.Label('Group')
        lbl_group.set_alignment(0, 0.5)
        tbl_user.attach(lbl_group, 0, 1, 3, 4, xpadding=8, ypadding=8)
        tbl_user.attach(combo_group, 1, 3, 3, 4, xpadding=8, ypadding=8)
        #
        d.vbox.pack_start(tbl_user)
        d.vbox.show_all()
        #
        ret = d.run()
        d.hide()

        if ret == gtk.RESPONSE_ACCEPT:
            uname = ent_uname.get_text().strip()
            rname = ent_rname.get_text().strip()
            passwd = ent_passwd.get_text().strip()
            passwd_md5 = md5new(passwd).hexdigest()
            group = combo_group.get_active_text()
            gid = 0
            if group:
                gid = self.get_group_id(group)

            if not uname:
                msg = 'User Name could not be left blank'
                error(parent=self.parent, message=msg,
                    title='Error')
            else:
                found = self.get_user_id(uname)
                if found:
                    msg = 'User %s already exists' %(uname)
                    error(message=msg, parent=d, title='Error')
                else:
                    q = '''
                    insert into users(user_name, real_name, gid, password)
                    values(?,?,?,?)
                    '''
                    a = (uname, rname, gid, passwd_md5)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=d)
                    #
                    self.draw_users()
        #
        d.destroy()

    def user_edit(self, widget):
        selection = self.trview_main.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            iter = iters[0]
            id = int(model.get_value(iter, 0))
            user = self.get_user(id)
            #
            d = gtk.Dialog('Edit User', self.parent, gtk.DIALOG_MODAL,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            d.set_size_request(self.app.main_win_width - 100, -1)

            tbl_user = gtk.Table(4, 3)
            #
            ent_uname = gtk.Entry()
            ent_uname.set_text(user[1])
            lbl_uname = gtk.Label('User Name')
            lbl_uname.set_alignment(0, 0.5)
            tbl_user.attach(lbl_uname, 0, 1, 0, 1, xpadding=8, ypadding=8)
            tbl_user.attach(ent_uname, 1, 3, 0, 1, xpadding=8, ypadding=8)
            #
            ent_rname = gtk.Entry()
            ent_rname.set_text(user[2])
            lbl_rname = gtk.Label('Real Name')
            lbl_rname.set_alignment(0, 0.5)
            tbl_user.attach(lbl_rname, 0, 1, 1, 2, xpadding=8, ypadding=8)
            tbl_user.attach(ent_rname, 1, 3, 1, 2, xpadding=8, ypadding=8)
            #
            ent_passwd = gtk.Entry()
            lbl_passwd = gtk.Label('Password (enter to change)')
            lbl_passwd.set_alignment(0, 0.5)
            tbl_user.attach(lbl_passwd, 0, 1, 2, 3, xpadding=8, ypadding=8)
            tbl_user.attach(ent_passwd, 1, 3, 2, 3, xpadding=8, ypadding=8)
            #
            combo_group = gtk.combo_box_new_text()
            group = self.get_group_name(user[3])
            self.group_populate_groups(combo=combo_group, active=group)
            lbl_group = gtk.Label('Group')
            lbl_group.set_alignment(0, 0.5)
            tbl_user.attach(lbl_group, 0, 1, 3, 4, xpadding=8, ypadding=8)
            tbl_user.attach(combo_group, 1, 3, 3, 4, xpadding=8, ypadding=8)
            #
            d.vbox.pack_start(tbl_user)
            d.vbox.show_all()
            #
            ret = d.run()
            d.hide()

            if ret == gtk.RESPONSE_ACCEPT:
                uname = ent_uname.get_text().strip()
                rname = ent_rname.get_text().strip()
                passwd = ent_passwd.get_text().strip()
                passwd_md5 = md5new(passwd).hexdigest()
                group = combo_group.get_active_text()
                gid = 0
                if group:
                    gid = self.get_group_id(group)

                if not uname:
                    msg = 'User Name could not be left blank'
                    error(parent=self.parent, message=msg,
                        title='Error')
                else:
                    found = self.get_user_id(uname)
                    if found and uname != user[1]:
                        msg = 'User %s already exists' %(uname)
                        error(message=msg, parent=d, title='Error')
                    else:
                        if passwd:
                            q = '''
                            update users set user_name=?, real_name=?, gid=?, password=?
                            where id=?
                            '''
                            a = (uname, rname, gid, passwd_md5, id)
                        else:
                            q = '''
                            update users set user_name=?, real_name=?, gid=?
                            where id=?
                            '''
                            a = (uname, rname, gid, id)
                        r = db_query(q, a, self.app.database)
                        if r[0] != 0:
                            msg = r[1]
                            dialog = error
                            dialog(title='Error', message=msg, parent=d)
                        #
                        self.draw_users()
            #
            #call external function when supplied
            #and when current user information is changed
            #act as bridge between status bar module
            #and user module
            if self.myuid == id:
                if self.external_func_user_edit:
                        self.external_func_user_edit(uname)
            d.destroy()


    def user_delete(self, widget):
        selection = self.trview_main.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            ids = [int(model.get_value(iter, 0)) for iter in iters]
            names = [model.get_value(iter, 1) for iter in iters]

            msg3 = '\n'
            if self.myuid in ids:
                try:
                    ids.remove(self.myuid)
                    names.remove(self.myname)
                except:
                    pass
                msg3 += '\nWarning: You can not delete yourself (removed from list).'

            if 1 in ids:
                try:
                    ids.remove(1)
                    uid1 = self.get_group(id=1)
                    names.remove(uid1[0][1])
                except:
                    pass
                msg3 += '\nWarning: You can not delete user with uid 1.'

            count = len(ids)
            info_delete_str = '\n'.join(names)
            #
            if count > 0:
                msg = 'Are you sure you want to '
                msg += 'delete %d names(s)?' %(count)
                msg2 = 'Selected user(s):\n' + info_delete_str
                msg2 += '\n\nAll corresponding data will also be deleted.'
                msg2 += '\nThis action can not be undone.'
                msg2 += msg3

                ok = confirm(title='Please confirm',
                    message=msg, message2=msg2, parent=self.parent,
                    buttons=gtk.BUTTONS_YES_NO)

                #if yes,
                if ok == gtk.RESPONSE_YES:
                    q = []
                    for id in ids:
                        query = 'delete from users where id=?'
                        args = (id,)
                        temp = (query, args)
                        q.append(temp)
                    r = db_query_transact(q, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=self.parent)
                    #
                    self.draw_users()


    def user_refresh(self, widget):
        self.draw_users()

    def group_edit_get_res(self, combo):
        group = combo.get_active_text()
        model_res = self.trview_res.get_model()
        model_res.clear()
        self.lbl_group_members.set_text('')
        if group:
            res = self.get_group_resources(group)
            resall = self.app.resource_all
            resall.sort()
            ent = []
            for ra in resall:
                if ra in res:
                    found=True
                else:
                    found=False
                temp = (found, ra)
                ent.append(temp)
            #
            for e in ent:
                model_res.append(e)
            #
            #
            members = self.get_group_members(group)
            members_info = 'Member count: %d' %(len(members))
            self.lbl_group_members.set_text(members_info)

    def group_edit_chk_toggle(self, widget, path):
        model = self.trview_res.get_model()
        iter = model.get_iter(path)
        if iter:
            active = not model.get_value(iter, 0)
            model.set_value(iter, 0, active)
        #

    def group_populate_groups(self, combo, active=''):
        groups = self.get_groups()
        groups_name = [x[1] for x in groups]
        #
        model = combo.get_model()
        model.clear()
        #
        combo.append_text('')
        i = 1
        activeindex = 0
        for g in groups_name:
            combo.append_text(g)
            if g == active:
                activeindex = i
            i += 1
        if active:
            combo.set_active(activeindex)
        else:
            combo.set_active(0)

    def group_rename(self, widget):
        group = self.combo_grp.get_active_text()
        if group:
            newgroup = input(title='Rename Group', label='New group name',
            parent=self.group_edit_dialog, default=group).strip().upper()
            if newgroup:
                groups = self.get_groups()
                found=False
                for g in groups:
                    if newgroup == g[1] and newgroup!=group:
                        found=True
                        break
                #
                if found:
                    msg = 'Group %s already exists' %(newgroup)
                    error(title='Error', message=msg,
                        parent=self.parent)
                else:
                    q = '''
                    update groups set group_name=? where group_name=?
                    '''
                    a = (newgroup, group)
                    r = db_query(q, a, self.app.database)
                    if r[0] != 0:
                        msg = r[1]
                        dialog = error
                        dialog(title='Error', message=msg, parent=self.group_edit_dialog)
                    else:
                        self.group_populate_groups(combo=self.combo_grp, active=newgroup)


    def group_new(self, widget):
        group = input(title='New Group', label='Group name',
            parent=self.group_edit_dialog).strip().upper()
        if group:
            groups = self.get_groups()
            found=self.get_group_id(group)
            #
            if found:
                msg = 'Group %s already exists' %(group)
                error(title='Error', message=msg,
                    parent=self.parent)
            else:
                q = '''
                insert into groups(group_name, resources)
                values(?,?)
                '''
                a = (group, '')
                r = db_query(q, a, self.app.database)
                if r[0] != 0:
                    msg = r[1]
                    dialog = error
                    dialog(title='Error', message=msg, parent=self.group_edit_dialog)
                else:
                    self.group_populate_groups(active=group, combo=self.combo_grp)



    def group_delete(self, widget):
        group = self.combo_grp.get_active_text()
        if group:
            gid = self.get_group_id(group)
            members = self.get_group_members(group)
            members_count = len(members)
            if members_count:
                msg = '''Group has %d member(s).\nAre you sure you want to delete group %s?\nAll users in this group will lose it's group information.''' %(
                members_count, group)
            else:
                msg = '''Are you sure you want to delete group %s?''' %(group)
            ok = confirm(title='Please confirm', message=msg,
                parent=self.group_edit_dialog, buttons=gtk.BUTTONS_YES_NO)
            if ok == gtk.RESPONSE_YES:
                q1 = '''
                update users set gid=0 where gid=?
                '''
                a1 = (gid,)
                q2 = '''
                delete from groups where id=?
                '''
                a2 = (gid,)
                q = ((q1, a1), (q2, a2))
                r = db_query_transact(q, self.app.database)
                if r[0] == 0:
                    msg = 'Group %s has been deleted successfully' %(group)
                    dialog = info
                else:
                    msg = r[1]
                    dialog = error
                dialog(title='Result', message=msg, parent=self.group_edit_dialog)
                #
                self.group_populate_groups(combo=self.combo_grp)
                self.combo_grp.popup()




    def group_save(self, widget):
        group = self.combo_grp.get_active_text()
        if group:
            gid = self.get_group_id(group)
            resall = []
            model = self.trview_res.get_model()
            iter = model.get_iter_first()
            while iter:
                temp = (model.get_value(iter, 0),
                        model.get_value(iter, 1))
                resall.append(temp)
                iter = model.iter_next(iter)
            real_resall = ','.join([x[1] for x in resall if x[0]])
            #
            q = '''
            update groups set resources=? where id=?
            '''
            a = (real_resall, gid)
            r = db_query(q, a, self.app.database)
            if r[0] == 0:
                msg = 'Settings for group %s have been saved successfully' %(group)
                dialog = info
            else:
                msg = r[1]
                dialog = error
            dialog(title='Result', message=msg, parent=self.group_edit_dialog)
            #



    def group_edit(self, widget):
        self.group_edit_dialog = gtk.Dialog('Group Editor',
            self.parent, gtk.DIALOG_MODAL,
            (gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.group_edit_dialog.set_size_request(
            self.width - 100, self.height - 100)
        #
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        #
        self.combo_grp = gtk.combo_box_new_text()
        self.group_populate_groups(combo=self.combo_grp)
        #
        lstore_res = gtk.ListStore(bool, str)
        self.trview_res = gtk.TreeView(lstore_res)
        trvcol_res_chk = gtk.TreeViewColumn('Select')
        trvcol_res_chk.set_min_width(60)
        trvcol_res_name = gtk.TreeViewColumn('Resource')
        trvcol_res_name.set_min_width(120)
        cell_res_chk = gtk.CellRendererToggle()
        cell_res_chk.set_property('activatable', True)
        cell_res_chk.connect('toggled', self.group_edit_chk_toggle)
        cell_res_name = gtk.CellRendererText()
        trvcol_res_chk.pack_start(cell_res_chk, True)
        trvcol_res_chk.set_attributes(cell_res_chk, active=0)
        self.trview_res.append_column(trvcol_res_chk)
        trvcol_res_name.pack_start(cell_res_name, True)
        trvcol_res_name.set_attributes(cell_res_name, text=1)
        self.trview_res.append_column(trvcol_res_name)
        lstore_res.clear()
        scrollw_res = gtk.ScrolledWindow()
        scrollw_res.set_policy(gtk.POLICY_AUTOMATIC,
            gtk.POLICY_AUTOMATIC)
        scrollw_res.add(self.trview_res)
        #
        vbox.pack_start(self.combo_grp, padding=4, expand=False)
        vbox.pack_start(scrollw_res, padding=4)
        #
        btnbox = gtk.VButtonBox()
        btnbox.set_spacing(10)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btn_save = gtk.Button(stock=gtk.STOCK_SAVE)
        btn_save.get_children()[0].get_children()[0].get_children()[1].set_text('Save settings')
        btn_save.connect('clicked', self.group_save)
        btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        btn_del.connect('clicked', self.group_delete)
        btn_rename = gtk.Button(stock=gtk.STOCK_EDIT)
        btn_rename.get_children()[0].get_children()[0].get_children()[1].set_text('Rename')
        btn_rename.connect('clicked', self.group_rename)
        btn_new = gtk.Button(stock=gtk.STOCK_NEW)
        btn_new.connect('clicked', self.group_new)
        btnbox.pack_start(btn_save)
        btnbox.pack_start(btn_rename)
        btnbox.pack_start(btn_del)
        btnbox.pack_start(btn_new)
        #
        self.lbl_group_members = gtk.Label()
        self.lbl_group_members.set_alignment(0.02, 0.5)
        #
        hbox.pack_start(vbox, padding=8)
        hbox.pack_start(btnbox, expand=False, padding=8)
        #
        self.combo_grp.connect('changed', self.group_edit_get_res)
        #
        self.group_edit_dialog.vbox.pack_start(hbox, padding=4)
        self.group_edit_dialog.vbox.pack_start(self.lbl_group_members, padding=4,
            expand=False)
        self.group_edit_dialog.vbox.show_all()
        #
        ret = self.group_edit_dialog.run()
        self.group_edit_dialog.destroy()
        #
        self.draw_users()
        return ret


#----------------------------------------------------------------------#
# ui_main.py                                                           #
#----------------------------------------------------------------------#
class UIMain:
    def __init__(self):
        #application
        self.app = Application()
        #

        #check for database existance, if not, build structure
        #
        if not os.path.exists(self.app.database) or os.path.getsize(self.app.database) == 0L:
            queries = self.app.init_db_query()
            for q in queries:
                r = db_query(q, (), self.app.database)
        #

        #
        settings = gtk.settings_get_default()
        settings.set_property('gtk-button-images', True)
        #

        #main window
        self.win = gtk.Window()
        self.win.set_title(self.app.main_title)
        self.win.set_position(gtk.WIN_POS_CENTER)
        #confirm or not
        self.win.connect('delete_event', self.main_quit)
        #self.win.connect('destroy', self.main_quit, None, False)
        #

        #gunakan modul yang ada, hanya ambil satu dua fungsinya saja
        #keren!!!
        #untuk login
        dummypassword = UIPassword(app=self.app)
        password_validator = dummypassword.validate_login
        login_ok = simple_login(validator=password_validator)
        if not login_ok[0]:
            sys.exit(1)
        else:
            self.username = login_ok[1]
        del dummypassword

        #setelah login, gunakan modul user, hanya untuk get uid, gid,
        #group, dan resources
        #keren!!!
        dummyuser = UIUser(app=self.app)
        self.uid = dummyuser.get_user_id(self.username)
        self.gid = dummyuser.get_user_group(self.username)
        self.group = dummyuser.get_group_name(self.gid)
        self.resources = dummyuser.get_group_resources(self.group)
        del dummyuser
        #

        #tabbed interface
        self.vb_tab = {} #dictionary to hold tabs
        self.nbook = gtk.Notebook()
        self.nbook.set_tab_pos(gtk.POS_TOP)
        for p in self.app.tabs:
            if p[0].upper() in self.resources:
                vb_temp = gtk.VBox()
                vb_temp.set_size_request(self.app.main_win_width,
                    self.app.main_win_height)
                hb_temp = gtk.HBox()
                img_file = p[1]
                img_temp = gtk.Image()
                img_temp.set_from_stock(img_file,
                    gtk.ICON_SIZE_LARGE_TOOLBAR)
                hb_temp.pack_start(img_temp)
                hb_temp.pack_start(gtk.Label(p[0]))
                hb_temp.show_all()
                self.nbook.append_page(vb_temp, hb_temp)
                self.vb_tab[p[0].upper()] = vb_temp

        #

        #get status bar from module
        self.statusbar = UIStatusBar(self.app.date_format,
            self.app.time_format, self.username, 1000)
        self.statusbar_ui = self.statusbar.create_ui()
        #

        #get ui from module
        if self.vb_tab.has_key('USER'):
            self.vb_user = self.vb_tab['USER']
            self.user = UIUser(app=self.app,
                parent=self.win,
                myuid=self.uid,
                myname=self.username,
                external_func_user_edit=self.statusbar.update_task)
            self.user_ui = self.user.create_ui()
            self.vb_user.pack_start(self.user_ui, expand=True)
        #

        #get ui from module
        if self.vb_tab.has_key('PRODUCT'):
            self.vb_product = self.vb_tab['PRODUCT']
            self.product = UIProduct(app=self.app,
                parent=self.win,
                myuid=self.uid,
                myname=self.username)
            self.product_ui = self.product.create_ui()
            self.vb_product.pack_start(self.product_ui, expand=True)
        #

        #get ui from module
        if self.vb_tab.has_key('CHANGE PASSWORD'):
            self.vb_password = self.vb_tab['CHANGE PASSWORD']
            self.password = UIPassword(app=self.app,
                parent=self.win,
                myuid=self.uid,
                myname=self.username)
            self.password_ui = self.password.create_ui()
            self.vb_password.pack_start(self.password_ui, expand=True)
        #

        #get ui from module
        if self.vb_tab.has_key('ABOUT'):
            self.vb_about = self.vb_tab['ABOUT']
            self.about = UIAbout(app=self.app, parent=self.win)
            self.about_ui = self.about.create_ui()
            self.vb_about.pack_start(self.about_ui, expand=True)
        #

        #main vbox
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.nbook)
        self.vbox.pack_start(self.statusbar_ui, expand=False)
        #

        #notebook signal handler, after all ui loaded
        self.nbook.connect('switch-page', self.nbook_switch_page)
        #

        #add main vbox, show all
        self.win.add(self.vbox)
        self.win.show_all()
        #


    def main_quit(self, widget, event=None, confirm=True):
        if confirm: #if confirmation set
            d = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                'Are you sure you want to quit?')
            d.set_title('Confirmation')
            ret = d.run()
            d.destroy()
            #
            if ret == gtk.RESPONSE_YES:
                self.main_quit(widget, event, False)
            else:
                return True
        else: # without confirmation
            gtk.main_quit()

    def nbook_switch_page(self, widget, page, page_num):
        tab = widget.get_nth_page(page_num)
        if tab:
            hb = widget.get_tab_label(tab)
            lbl = hb.get_children()[1]
            title = lbl.get_text().upper()
            if title == 'USER':
                self.user.draw_users()
            elif title == 'PRODUCT':
                self.product.draw_products()
            elif title == 'ABOUT':
                pass
            else:
                pass


#----------------------------------------------------------------------#
# simplestock.py                                                       #
# No more dependency check                                             #
#----------------------------------------------------------------------#
if __name__ == '__main__':
    ui_main = UIMain()
    gtk.main()

