#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.uio.ifi.bjarneh.cl.main

this is where it all starts, by parsing input arguments, and
then afterwards reading input from inputfile and converting
it to a Maude module and proving theorems hopefully..
"""

import sys      # command line arguments and output
import os       # needed by 'Main.which' and pathwalk
import re       # regular expressions
import tempfile # needed to construct temporary files for Maude modules
from no.uio.ifi.bjarneh.parse.cmdline import GetOpt      # parse sys.argv
from no.uio.ifi.bjarneh.cl.parse.Parser import Parser    # parse theory
from no.uio.ifi.bjarneh.cl.template.filler import Filler 
from no.uio.ifi.bjarneh.util.subprocess import SubProcess


__author__='bjarneh@ifi.uio.no'
__version__='monologue : 0.01' 


class Main(object):
    """
    monologue - theorem prover for geometric logic

    usage: monologue [OPTIONS] somefile.gl

    Maude version >= 2.4 is required for this to work
    if '-' is given as input file stdin will be read
    all boolean options default to false, and options
    which require a value have their default written
    inside [ brackets ] after the explanation

    options:

    -h  --help              print this menu and exit
    -v  --version           print version and exit
    -d  --dump              dump Maude module to output        
    -r  --recursive         investigate recursively
    -p  --print             turn on Maude print statements
    -n  --no-escape         turn off escape sequences     
    -l  --level             how deep in terms of iterations   [        100 ]
    -t  --timeout           timeout value in seconds          [        3.0 ]
    -o  --output            where to send output              [ sys.stdout ]
    -m  --maude             specify another Maude location    [       NULL ]
    
    """
    
    defaults = {}           # default settings
    defaults['mode']        = 'PROVEINPUT'
    defaults['escape']      = 1
    defaults['timeout']     = 3.0   # seconds
    defaults['print']       = 0
    defaults['output']      = sys.stdout
    defaults['level']       = 100
    defaults['recursive']   = 0
    defaults['dump']        = 0
    defaults['Maude']       = "maude"
    defaults['input']       = []


    def __init__(self, argv):
        """ parse input arguments, and start up"""
        self.parseArgv(argv)
        self.start()


    def parseArgv(self, argv):
        """ 
        parse input arguments, self.defaults dictionary holds
        the default values, which are overwritten by command line
        options if given
        """

        getopt = GetOpt()

        getopt.add_bool_option(['-h', '-help', '--help', '?'])
        getopt.add_bool_option(['-v', '-version', '--version'])
        getopt.add_bool_option(['-d', '-dump', '--dump'])
        getopt.add_bool_option(['-p', '--print', '-print'])
        getopt.add_bool_option(['-n', '--no-escape', '-no-escape'])
        getopt.add_bool_option(['-r','--recursive','-recursive'])
        getopt.add_str_option( ['-l', '-level', '--level','--level=', '-timeout='], 
                              test=(lambda x : re.match(r"^\d+$", x) and int(x) < 1000),
                              errormsg=" -level: must be number in range [1,1000]")
        getopt.add_str_option( ['-t', '-timeout', '-timeout','--timeout',
                               '-timeout=','--timeout='], 
                              test=lambda x : re.match(r"^\d*\.?\d+$", x) ,
                              errormsg=" -timeout: value must be number ")
        getopt.add_str_option( ['-o','--output','-output','-output=','--output='])
        getopt.add_str_option( ['-m','--maude','-maude','-maude=','--maude='])

        try:
            (opts, args) = getopt.parse(argv)
        except Exception, inst:
            sys.stderr.write(str(inst) + '\n')
            sys.exit(1)

        keys = opts.keys()

        if('-h' in keys):   self.defaults['mode']      = 'HELP'
        if('-v' in keys):   self.defaults['mode']      = 'VERSION'            
        if('-d' in keys):   self.defaults['dump']      = 1
        if('-t' in keys):   self.defaults['timeout']   = float(opts['-t'][0])
        if('-o' in keys):   self.defaults['output']    = open(opts['-o'][0],'w')
        if('-p' in keys):   self.defaults['print']     = 1
        if('-l' in keys):   self.defaults['level']     = int(opts['-l'][0])
        if('-n' in keys):   self.defaults['escape']    = 0
        if('-r' in keys):   self.defaults['recursive'] = 1
        if('-m' in keys):   self.defaults['Maude']     = opts['-m'][0]

        self.sanityCheck()
                                     
        self.defaults['input'] = args

    def sanityCheck(self):
        """ remove funky combinations of options"""
        # when writing to file we don't want hashbar as well
        if not self.defaults['output'] == sys.stdout:
            if self.defaults['escape']:
                self.defaults['escape'] = 0
        # with print statements we don't want hashbar as well
        if self.defaults['print'] and self.defaults['escape']:
            self.defaults['escape'] = 0


    def start(self):
        """ start doing whatever user wants to do"""

        mode = self.defaults['mode']

        if  (mode == 'PROVEINPUT'):  self.inputLoop()
        elif(mode == 'HELP'):        self.help()
        elif(mode == 'VERSION'):     self.version()

        sys.exit(1) # should not come to this..

    
    def inputLoop(self):
        """ traverse all input files/directories and try to prove them"""

        for inputfile in self.defaults['input']:
            if self.defaults['recursive'] and os.path.isdir(inputfile) :
                os.path.walk(inputfile, self.walker, None)
            else:
                self.parseAndProve(inputfile)

        if not self.defaults['output'] == sys.stdout:
            self.defaults['output'].close()

        sys.exit(0)


    def parseAndProve(self, inputfile):
        """ hopefully the name says it all.. """

        mm = self.getMaudeModule(inputfile)
        if self.defaults['dump']:
            if self.defaults['print']:
                mm = self.removePrintComments(mm)
            self.defaults['output'].write(mm)
        else:
            self.prove(mm)


    def walker(self, arg, dirname, fnames):
        """ pathwalk directory recursively """
        completenames = [ dirname + os.sep + a for a in fnames ]
        for filename in completenames:
            if os.path.isfile(filename):
                self.parseAndProve(filename)


    def prove(self, MaudeModule):
        """ try to locate a useful Maude install and start up
        a subprocess which takes our generated module as input,
        and naturally tries to prove it"""

        whichMaude = Main.which(self.defaults['Maude'])
        if not whichMaude:
            sys.stderr.write("[ERROR] excutable Maude not found \n")
            sys.exit(1)
        else:
            (fd, fname) = tempfile.mkstemp(suffix=".maude",
                                           prefix="monologue-", 
                                           text=1)
            if self.defaults['print']:
                if self.versionCheck(whichMaude):
                    MaudeModule = self.removePrintComments(MaudeModule)

            os.write(fd, MaudeModule)
            os.close(fd)
            args = []
            args.append('-no-banner')
            args.append('-no-ansi-color')
            args.append(fname)
            child = SubProcess(whichMaude,
                               args,
                               self.defaults['escape'],
                               self.defaults['timeout'],
                               self.defaults['output'])
            child.start()
            #TODO subprocess(whichMaude, args, escape, timeout)
            os.unlink(fname)


    def versionCheck(self, whichMaude):
        """ we need version 2.4 or better to do uncomment print statements """

        version = SubProcess.spoof(whichMaude + " --version").strip()
        
        if re.match("^\d+\.\d+$", version):
            if float( version ) < 2.4:
                sys.stderr.write("[WARNING] your Maude version has no 'print' statement\n")
                return 0
        else:
            if re.match("^alpha.*$", version):
                sys.stderr.write("[WARNING] your are running an Alpha version\n") 
                sys.stderr.write("[WARNING] it may not support 'print' statement\n") 
                sys.stderr.write("[WARNING] do this at your own risk\n")
        return 1


    def removePrintComments(self, MaudeModule):
        """ remove comments which will make print statements active"""
        return re.sub("-----", "", MaudeModule)


    def getMaudeModule(self, inputfile):
        """ parse inputfile and construct a Maude module """
    
        if not self.defaults['dump']:
            if inputfile == '-':
                self.defaults['output'].write("input file  :  stdin\n")
            else:
                bname = os.path.basename(inputfile)
                self.defaults['output'].write("input file  :  %s\n"%(bname))

        parser = Parser()
        theory = parser.parseTheory(inputfile)

        # filler == TemplateFiller
        filler = Filler(theory)
       
        setPrintOn = "set print attribute on ."
       
        if not self.defaults['print']:
            setPrintOn = "--- no print attribute "

        return filler.getMaudeModule(self.defaults['level'],
                                     setPrintOn)


    def help(self):
        """ print help message (help is self.__doc__) """
        for line in self.__doc__.split("\n"):
            sys.stdout.write(line[3:]+'\n')
        sys.exit(0)


    def version(self):
        """ print version and exit """
        sys.stdout.write( __version__ + '\n')
        sys.exit(0)


    @staticmethod
    def which(executable):
        """ 
        checks whether the executable can be 
        found in PATH (modified from pexpect) 
        """
    
        # executable already contains a path.
        if os.path.dirname(executable) != '':
            if os.access (executable, os.X_OK):
                return executable
    
        if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
            p = os.defpath
        else:
            p = os.environ['PATH']
    
        pathlist = p.split(os.pathsep)
    
        for path in pathlist:
            f = os.path.join(path, executable)
            if os.access(f, os.X_OK):
                return f
        return None


if __name__ == '__main__':
    pass
