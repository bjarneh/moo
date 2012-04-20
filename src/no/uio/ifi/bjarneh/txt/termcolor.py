#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
no.uio.ifi.bjarne.txt.termcolor

this class returns some escape strings and info which
can be used to create simple terminal based effects

    colors
    reverse
    bold,
    underline,
    blink
    clear   (screen/line)
    hide cursor
    width   (of terminal)
    height  (of terminal)

"""

__author__  = "bjarneh@ifi.uio.no"
__version__ = "termcolor.py 1.0"

#_______________________________________________________________________________

            
class TermColor:
    
    """
    TermColor                                      
                                                 
    heavily inspired by TerminalController.py      
    part of epydoc. this class is a bit less fancy 
    """

    def __init__(self, setFancy=1):

        self.fancy = 1
        self.effect = {}

        try:
            import sys,curses
            curses.setupterm()
            if not sys.stdout.isatty():
                raise Exception()
        except: # if an exception is thrown we are !fancy
            self.fancy = 0
            self.effect['cols'] = 80
            self.effect['lines'] = 24
    
 
        self.effect['cols']      = curses.tigetnum('cols') or 80
        self.effect['lines']     = curses.tigetnum('lines') or 24

        if(not (setFancy and self.fancy)):
            self.fancy = 0; return


        self.effect['clear']     = curses.tigetstr('clear') or ''
        self.effect['clear_bol'] = curses.tigetstr('el1') or ''
        self.effect['bol']       = curses.tigetstr('cl') or '' 
        self.effect['up']        = curses.tigetstr('cuu1') or ''
        self.effect['hide_curs'] = curses.tigetstr('civis') or ''
        self.effect['show_curs'] = curses.tigetstr('cnorm') or ''
        self.effect['clear_eol'] = curses.tigetstr('el') or ''
        self.effect['reverse']   = curses.tigetstr('rev') or ''
        self.effect['bold']      = curses.tigetstr('bold') or ''
        self.effect['blink']     = curses.tigetstr('blink') or ''
        self.effect['normal']    = curses.tigetstr('sgr0') or ''
        self.effect['underline'] = curses.tigetstr('smul') or ''

        colors = "black;blue;green;cyan;red;magenta;yellow;white".split(";")
        
        set_fg = curses.tigetstr('setf')
        set_bg = curses.tigetstr('setb')

        if(set_fg):
            for i,key in enumerate(colors):
                self.effect["fg_"+key] = curses.tparm(set_fg, i)

        if(set_bg):
            for i,key in enumerate(colors):
                self.effect["bg_"+key] = curses.tparm(set_bg, i)


    def isFancy(self):
        """ return true if terminal has ability to understand escape sequences """
        return self.fancy

    def get(self, param):
        """ get escape sequense, example: get('fg_blue+bg_black+bold') """
        if(not self.isFancy() and not param.lower() in ['cols', 'lines']): return ''
        param = str(param)
        param = param.lower()
        ret_effect = ''

        if('+' in param):
            params = param.split('+')
            for p in params:
                if(p.strip() in self.effect.keys()):
                    ret_effect += self.effect[p.strip()]
        
        elif(param in self.effect.keys()):
            ret_effect = self.effect[param]
        
        return ret_effect 


#_______________________________________________________________________________

if __name__ == '__main__':
    pass
