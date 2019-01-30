#!/usr/bin/env python

#Simple Bar Chart using PyGTK
#(c) Noprianto <nop@noprianto.com>, 2009, GPL
#

import math
import random
import pygtk
pygtk.require('2.0')
import gtk
import cairo


class Main:
    def __init__(self):
        self.data = [('Jan', 100), ('Feb', 150), ('Mar', 95), ('Apr', 120)]
        self.border = 40
        self.step = 10 #todo: fix step 
        self.font_size = 10
        #
        self.win = gtk.Window()
        self.win.set_title('Simple Bar Chart')
        self.win.set_size_request(400, 400)
        self.win.connect('destroy', gtk.main_quit)
        #
        self.draw = gtk.DrawingArea()
        self.draw.connect('expose-event', self.draw_expose)
        #
        self.win.add(self.draw)
        self.win.show_all()
    
    def draw_expose(self, widget, event):
        self.draw_bar_chart(widget) #quick and dirty 

    def draw_bar_chart(self, widget):
        cr = widget.window.cairo_create()
        cr.set_line_width(0.3)
        #
        cr.set_source_rgb(1.0, 1.0, 1.0)
        w = self.win.allocation.width-self.border
        h = self.win.allocation.height-self.border
        cr.rectangle(self.border/2, self.border/2, w, h)
        cr.fill()
        #
        max_val = max([x[1] for x in self.data])
        item_width = w/len(self.data)
        item_delta = 10
        #
        cr.select_font_face('Courier', cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(self.font_size)
        posy = self.border/2
        dy = h/(max_val/self.step)
        for i in range(max_val, -1, -self.step):
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.move_to(self.border/2, posy)
            cr.line_to((self.border/2)+w, posy)
            cr.stroke()
            #
            cr.set_source_rgb(0.0, 0.0, 1.0)
            cr.move_to(0, posy)
            value = str(i).rjust(len(str(max_val)))
            cr.show_text(value)
            posy = posy + dy
        #
        counter = 0
        cr.translate((self.border/2)+(item_delta/2), posy-dy)
        for d in self.data:
            posx = counter*item_width
            item_height = -dy*(float(d[1])/self.step)
            cr.set_source_rgb(random.random(), random.random(),
                random.random())
            cr.rectangle(posx, 0, item_width-item_delta, item_height)
            cr.fill()
            #
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.move_to(posx, self.font_size)
            cr.show_text(d[0])
            #
            counter = counter+1
            
if __name__ == '__main__':
    app = Main()
    gtk.main()
