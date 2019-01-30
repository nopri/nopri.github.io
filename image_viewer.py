#!/usr/bin/env python

#Simple Image Viewer, with slideshow 
#(c) Noprianto <nop@noprianto.com>, 2009, GPL
#

#usage: image_viewer.py <interval> <pattern1> [pattern2] ... [patternn]
#set interval to 0 to disable slideshow
#

import os
import sys
import glob
#
import gtk
import gobject


class Main:
    def __init__(self, interval, images):
        self.images = images
        self.index = -1
        self.interval = interval
        #
        self.win = gtk.Window()
        self.win.set_title('Image Viewer')
        self.win.connect('destroy', self.quit)
        #
        self.img = gtk.Image()
        #
        self.btn_prev = gtk.Button(stock=gtk.STOCK_MEDIA_PREVIOUS)
        self.btn_prev.connect('clicked', self.navigate, -1)
        self.btn_next = gtk.Button(stock=gtk.STOCK_MEDIA_NEXT)
        self.btn_next.connect('clicked', self.navigate, 1)
        self.btnbox = gtk.HButtonBox()
        self.btnbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.btnbox.set_spacing(10)
        self.btnbox.pack_start(self.btn_prev)
        self.btnbox.pack_start(self.btn_next)
        #
        self.statb = gtk.Statusbar()
        #
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.img, expand=True, padding=2)
        self.vbox.pack_start(self.btnbox, expand=False, padding=2)
        self.vbox.pack_start(self.statb, expand=False, padding=2)
        #
        self.win.add(self.vbox)
        self.btn_next.clicked()
        self.win.show_all()
        #
        if self.interval > 0:
            self.tid = gobject.timeout_add(self.interval, self.slide_show)
    
    def quit(self, widget):
        try:
            gobject.source_remove(self.tid)
        except:
            pass
        gtk.main_quit()
    
    def navigate(self, widget, step):
        self.index += step
        fname = self.images[self.index]
        #
        go_next = False
        #
        if self.index < 1:
            self.btn_prev.set_sensitive(False)
        else:
            self.btn_prev.set_sensitive(True)
        #
        if self.index > len(self.images) - 2:
            self.btn_next.set_sensitive(False)
        else:
            self.btn_next.set_sensitive(True)
            go_next = True
        #
        self.img.set_from_file(fname)
        self.statb.push(1, fname)
        #
        return go_next
    
    def slide_show(self):
        ret = self.navigate(None, 1)
        return ret
    
        
if __name__ == '__main__':
    images = []
    if len(sys.argv) < 3:
        print '%s <interval> <pattern1> [pattern2] ... [patternn]' %(
        sys.argv[0])
    else:
        try:
            interval = int(sys.argv[1])
        except:
            interval = 0
        #
        pats = sys.argv[2:]
        for p in pats:
            files = glob.glob(p)
            for f in files:
                images.append(os.path.abspath(f))
        #
        if images:
            app = Main(interval, images)
            gtk.main()
        else:
            print 'No files found'
            
