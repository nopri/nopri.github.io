#!/usr/bin/env python

#Simple Syntax Highlighting Demo
#(c) Noprianto <nop@noprianto.com>, 2009, GPL
#

import gtk
import keyword

class Main:
    def __init__(self):
        self.win = gtk.Window()
        self.win.connect('destroy', gtk.main_quit)
        self.win.set_title('Simple Syntax Highlighting Demo')
        #
        self.textb = gtk.TextBuffer()
        self.textb.connect('changed', self.keyword_check)
        self.tag = self.textb.create_tag('fg_blue', 
            foreground='blue')
        #
        self.textv = gtk.TextView(self.textb)
        self.textv.set_size_request(400, 320)
        self.scrollw = gtk.ScrolledWindow()
        self.scrollw.set_policy(gtk.POLICY_AUTOMATIC, 
            gtk.POLICY_AUTOMATIC)
        self.scrollw.add(self.textv)
        #
        self.win.add(self.scrollw)
        self.win.show_all()
    
    def keyword_check(self, widget):
        pos = widget.get_property('cursor-position')
        iter_cur = widget.get_iter_at_offset(pos-1)
        c_cur = iter_cur.get_char()
        if not c_cur.strip():
            word_list = []
            pos_temp = pos-1
            while True:
                pos_temp -= 1
                iter_temp =  widget.get_iter_at_offset(pos_temp)
                c_temp = iter_temp.get_char()
                if not c_temp.strip() or pos_temp == -1:
                    if pos_temp < 1: 
                        iter_temp = widget.get_start_iter()
                    break
                else:
                    word_list.insert(0, c_temp)
            #
            word = ''.join(word_list).strip()
            if word in keyword.kwlist:
                widget.apply_tag(self.tag, iter_temp, iter_cur)
            else:
                widget.remove_tag(self.tag, iter_temp, iter_cur)
        
        
if __name__ == '__main__':
    app = Main()
    gtk.main()
