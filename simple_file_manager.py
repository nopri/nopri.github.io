#!/usr/bin/env python

#very simple GTK-based file manager
#(c) Noprianto <nop@noprianto.com>, 2009, GPL
#

import sys
import os
import shutil
import distutils.dir_util
import gtk
import gobject


class Main:
    def __init__(self, directory):
        self.curdir = os.path.abspath(directory)
        #
        self.win = gtk.Window()
        self.win.set_title(self.curdir)
        self.win.connect('destroy', self.quit)
        #
        self.vbox = gtk.VBox()
        #
        self.btnc = gtk.Button(self.curdir)
        self.btnc.set_use_underline(False)
        self.btnc.connect('clicked', self.select_dir)
        #
        self.lstore = gtk.ListStore(str, str, str)
        self.trview = gtk.TreeView(self.lstore)
        self.trview.set_size_request(600, 400)
        self.trview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.tvcol_type = gtk.TreeViewColumn('Type')
        self.tvcol_type.set_min_width(60)
        self.tvcol_fname = gtk.TreeViewColumn('File Name')
        self.tvcol_fname.set_min_width(400)
        self.tvcol_info = gtk.TreeViewColumn('Link Target')
        self.trview.append_column(self.tvcol_type)
        self.trview.append_column(self.tvcol_fname)
        self.trview.append_column(self.tvcol_info)
        self.cell_type = gtk.CellRendererPixbuf()
        self.cell_fname = gtk.CellRendererText()        
        self.cell_info = gtk.CellRendererText()
        self.tvcol_type.pack_start(self.cell_type)
        self.tvcol_fname.pack_start(self.cell_fname)
        self.tvcol_info.pack_start(self.cell_info)
        self.tvcol_type.set_attributes(self.cell_type, stock_id=0)
        self.tvcol_fname.set_attributes(self.cell_fname, text=1)
        self.tvcol_info.set_attributes(self.cell_info, text=2)
        self.scrollw = gtk.ScrolledWindow()
        self.scrollw.set_policy(gtk.POLICY_AUTOMATIC, 
            gtk.POLICY_AUTOMATIC)
        self.scrollw.add(self.trview)        
        #
        self.btn_del = gtk.Button(stock=gtk.STOCK_DELETE)
        self.btn_del.connect('clicked', self.action_del)
        self.btn_copyto = gtk.Button(stock=gtk.STOCK_COPY)
        self.btn_copyto.connect('clicked', self.action_copyto)
        #
        self.btnbox = gtk.HButtonBox()
        self.btnbox.set_layout(gtk.BUTTONBOX_START)
        self.btnbox.set_spacing(2)
        self.btnbox.pack_start(self.btn_del)
        self.btnbox.pack_start(self.btn_copyto)
        #
        self.vbox.pack_start(self.btnc, expand=False, padding=2)
        self.vbox.pack_start(self.scrollw, expand=True, padding=2)
        self.vbox.pack_start(self.btnbox, expand=False, padding=2)
        #
        self.listdir()
        self.tid = gobject.timeout_add(2000, self.listdir)
        #
        self.win.add(self.vbox)
        self.win.show_all()
    
    def quit(self, widget):
        if self.tid:
            gobject.source_remove(self.tid)
        gtk.main_quit()
            
    def select_dir(self, widget):
        fcd = gtk.FileChooserDialog(parent=self.win,
            action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
            title='Select directory')
        
        ret = fcd.run()
        if ret == gtk.RESPONSE_OK:
            temp = fcd.get_current_folder()
            if temp != self.curdir:
                self.lstore.clear()
                self.curdir = temp
                widget.set_label(self.curdir)
                self.win.set_title(self.curdir)
        #
        fcd.destroy()
    
    def action_del(self, widget):
        selection = self.trview.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            d = gtk.MessageDialog(parent=self.win, 
                type=gtk.MESSAGE_QUESTION,
                buttons=gtk.BUTTONS_OK_CANCEL)
            d.set_markup('''Are you sure you want to delete %d file(s)?
            ''' %(len(iters)))
            ret = d.run()
            if ret == gtk.RESPONSE_OK:
                for i in iters:
                    fname = model.get_value(i, 1)
                    absf = self.curdir + os.path.sep + fname
                    if os.path.isdir(absf):
                        shutil.rmtree(absf)
                    else:
                        os.unlink(absf)
            #            
            d.destroy()
    
    def action_copyto(self, widget):
        selection = self.trview.get_selection()
        model, selected = selection.get_selected_rows()
        iters = [model.get_iter(path) for path in selected]
        if iters:
            d = gtk.Dialog(parent=self.win, 
                title='Select destination directory',
                buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            fcd = gtk.FileChooserButton('Select destination directory')
            fcd.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
            d.vbox.pack_start(fcd, padding=2)
            d.show_all()
            ret = d.run()
            if ret == gtk.RESPONSE_OK:
                dest = fcd.get_current_folder()
                if os.path.exists(dest):
                    for i in iters:
                        fname = model.get_value(i, 1)
                        absf = self.curdir + os.path.sep + fname
                        if os.path.isdir(absf):
                            distutils.dir_util.copy_tree(absf, dest)
                        else:
                            shutil.copy(absf, dest)
                else:
                    d2 = gtk.MessageDialog(parent=self.win, 
                        type=gtk.MESSAGE_ERROR,
                        buttons=gtk.BUTTONS_OK,
                        message_format='''
                            Destination directory does not exists!''')
                    d2.run()
                    d2.destroy()
            d.destroy()
                                                
    def listdir(self):
        #get all files in current directory
        all = []
        try:
            files = os.listdir(self.curdir)
        except:
            files = []
        files.sort()
        for f in files:
            absf = self.curdir + os.path.sep + f
            stock = gtk.STOCK_FILE
            target = ''
            if os.path.isdir(absf):
                stock = gtk.STOCK_DIRECTORY
            elif os.path.isfile(absf):
                if os.path.islink(absf):
                    stock = gtk.STOCK_GO_FORWARD
                    target = os.readlink(absf)
            all.append((stock, f, target))
        #extract only filename from 'all'
        allfilenames = [x[1] for x in all]
        #
        #update treeview
        #get current entries and it's treerowref
        prevfiles = []
        iter = self.lstore.get_iter_first()
        while iter:
            fname = self.lstore.get_value(iter, 1) #fname
            path = self.lstore.get_path(iter)
            rowref = gtk.TreeRowReference(self.lstore, path)
            prevfiles.append([fname, rowref])
            iter = self.lstore.iter_next(iter)
        #        
        #if file names are not valid anymore (not in 'allfilenames')
        #lets remove the row
        for i in prevfiles:
            if i[0] not in allfilenames:
                path = i[1].get_path()
                iter = self.lstore.get_iter(path)
                self.lstore.remove(iter)
                prevfiles.remove(i)
        #        
        #current entries are now valid
        prevfilenames = [x[0] for x in prevfiles]
        #
        #if there are new files to add        
        for i in all:
            if i[1] not in prevfilenames:
                self.lstore.append(i)
        #
        return True
        

if __name__ == '__main__':
    directory = '.'
    if len(sys.argv) > 1:
        check = sys.argv[1]
        if os.path.exists(check):
            directory = check
    #
    app = Main(directory)
    gtk.main()
