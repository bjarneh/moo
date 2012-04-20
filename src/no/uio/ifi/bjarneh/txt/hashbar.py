#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.uio.ifi.bjarne.txt.hashbar

sometimes its handy to have a hashbar to make the user
see that the programme is actually doing something,
and its not just stuck in a infinite loop. a hashbar
gives this illusion, and since this is a text-based
program we really need to make a text-based hashbar.
this can only be done with the use of ncurses since
this is the only way to figure out how wide the
terminal is and so on. and since the program should
do other things besides showing a hashbar it extends
the threading.Thread class.

example:

    # timeout value is here 2.2 seconds
    # foreground set to yellow and bold

    hashbar = HashBar(2.2, 'fg_yellow+bold')
    hashbar.start()

    callSomeFunction(args)   # do something useful 

    hashbar.finished.getDone()
    hashbar.join()

"""

import threading
import time
import sys

from no.uio.ifi.bjarneh.txt.termcolor import TermColor

#_______________________________________________________________________________


class Finito(object):
    """
    small class to help spoof off a thread
    to draw the hash/progress bar
    """
    def __init__(self):
        self.fin = 0

    def getDone(self):
        self.fin = 1

    def isDone(self):
        return self.fin

#_______________________________________________________________________________

class DefaultFormat(object):
    def __init__(self):
        pass

    @staticmethod
    def getFormat(format=None):
        termcolor = TermColor()
        if termcolor.isFancy():
            fmts = {}
            fmts['CLEAR']  = termcolor.get('up+bol+clear_eol')
            fmts['NORMAL'] = termcolor.get('show_curs+normal')
            fmts['WIDTH']  = termcolor.get('cols')

            if(format):
                fmts['FORMAT'] = termcolor.get(format + '+hide_curs')
            else:
                fmts['FORMAT'] = termcolor.get('hide_curs')

            return fmts
        return None

#_______________________________________________________________________________

class HashBar(threading.Thread):

    def __init__(self, timeout, format=None):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.finished = Finito()
        self.fmts = DefaultFormat.getFormat(format)

    def stop(self):
        self.finished.getDone()

    def run(self):

        if not self.fmts: return # no escape capabilities

        elapse = float(self.timeout)/100

        FORMAT = self.fmts['FORMAT']
        CLEAR  = self.fmts['CLEAR']
        NORMAL = self.fmts['NORMAL']
        WIDTH  = self.fmts['WIDTH']

        sys.stdout.write(FORMAT)

        header = "Timeout".center(WIDTH)
        hbar_width = WIDTH - 11;

        cnt = 0.0

        if(hbar_width < 1):
            sys.stdout.write(NORMAL)
            self.finished.active = 0
            return

        while(cnt < self.timeout and (not self.finished.isDone())):
            sys.stdout.write("\n"+header+"\n")
            pst = cnt/self.timeout
            bar = "%3d%% "% float(100*pst)
            progress = int((hbar_width*pst))
            bar += "[%s%s] "% ("="*progress, "-"*(hbar_width - progress))
            sys.stdout.write(bar.center(WIDTH)+"\n")
            time.sleep(elapse)
            sys.stdout.write(CLEAR*3)
            cnt += elapse

        # restore terminal
        sys.stdout.write(NORMAL)
        self.finished.active = 0
        return
        
    
#_______________________________________________________________________________


if __name__ == '__main__':
   pass 
