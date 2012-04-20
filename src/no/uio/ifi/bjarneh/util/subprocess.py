#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
subprocess.py

this class is basically just a wrapper for functionality found
in org.noah.pexpect, which is able to duplicate stdout and
stdin and use these as sockets to communicate with subprocesses.

when processes are run, you can specify that you would like
to wait for a maximum period of time before killing child
process, and you can also specify that you want a hashbar.
"""

from org.noah.pexpect import pexpect
from no.uio.ifi.bjarneh.txt.hashbar import HashBar


__author__  = "bjarneh@ifi.uio.no"
__version__ = "subprocess.py 1.0"


class SubProcess(object):
    """
    this class starts a subprocesses, for this
    application the most important process is Maude
    naturally....
    """

    def __init__(self, cmd, args, hashbar, timeout, output):
        self.timeout = timeout
        self.hb = hashbar
        self.cmd = cmd
        self.args = args
        self.output = output


    @staticmethod
    def spoof(dowhat):
        """ just run a command and return result """
        result = None
        try: 
            result = pexpect.run(dowhat)
        except: pass
        return result

    def start(self):
        if self.hb:
            self.hashBarSpawn()
        else:
            self.noHashBarSpawn()

    def hashBarSpawn(self):

        tred = HashBar(self.timeout, None)
        tred.start()
        result = None
        fail   = None
        child  = None
        
        try:
            child = pexpect.spawn(self.cmd, args=self.args, timeout=self.timeout)
            child.expect("(rewrites: .*)Bye")
            result = str(child.match.groups()[0])
        except:
            fail = "[TIMEOUT]\n"
            if child and child.isalive():
                child.terminate(force=1)

##         tred.finished.getDone()
        tred.stop()
        tred.join()

        if result : self.output.write(result)
        if fail   : self.output.write(fail)


    def noHashBarSpawn(self):
        child = None
        try:
            child = pexpect.spawn(self.cmd, args=self.args, 
                                  timeout=self.timeout, logfile=self.output)
            child.expect(pexpect.EOF)
        except:
            self.output.write("[TIMEOUT] \n")
            if child and child.isalive():
                child.terminate(force=1)


    
# end Subprocess


if __name__ == '__main__':
    pass
