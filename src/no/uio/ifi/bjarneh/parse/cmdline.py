#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.uio.ifi.bjarneh.parse.cmdline


getopt lacks the ability to do any testing of arguments
as they are parsed, so i just thought that i should write
something which provides that. the ability to control
exactly what each option should be with one large list or
so is in my opinion better than the typical 'short options'
'long options' stuff. i.e., simple initialization is worth
less than complete control  :-)
optparse fails to support long options starting with
a single '-', and i did not want to fiddle with another 
module when such a program is rather easy to implement.

---------------- why? ---------------------

typical getopt use:

import getopt, sys

try:
    (ops, arg) getopt.getopt(sys.argv[1:], 'hvf:', ['help', 'version', 'file='])
except:
    print usage


for o, a in ops:
    if o in ('-h', '--help'):
        print "help is on the way"
    elif o in ('-f', '--file'):
        file = a


# and so on...



typical GetOpt use:


from cmdline import GetOpt

getopt = GetOpt()

getopt.add_bool_option(['-h', '-help', '--help']))
getopt.add_bool_option(['-v', '-verbose', '--verbose'])
getopt.add_str_option(['-f', '-file', '-file=', '--file', '--file='], test=lambda x : os.path.isfile(x))


try:
    (ops, arg) = getopt.parse(sys.argv[1:])
except:
    print usage

keys = ops.keys()

if('-h' in keys):
    print "help"

if('-f' in keys):
    print "--file ", ops['-f']


# and so on


---------------- howto -------------------

 

verbose example:


  import sys, re, os
  from go import GetOpt
  

  getopt = GetOpt()

  getopt.add_bool_option(['-h', '-help', '--help'])
  getopt.add_bool_option(['-v', '-version', '--version'])

  # we require trailing arguments to be actual files

  getopt.add_str_option(['-f', '-f=', '-file', '-file=', '--file', '--file='], 
                        test=lambda x : os.path.isfile(x), errormsg="'-file' needs a real filename")

  # we require trailing arguments to be directories

  getopt.add_str_option(['-d', '-d=', '-dir', '-dir=', '--dir', '--dir='],  test=lambda x : os.path.isdir(x))

  # this option can have as many trailing arguments as it wants, since trailing is set to -1
  # example: 
  #         
  #  -I/some/lib -I /some/other/lib /also/a/lib /lib/me/backwards

  getopt.add_str_option('-I', trailing=-1, test=lambda x : os.path.isdir(x)) 



  # GetOpt.__str__() returns the options formattet, so it can be used like this

  usage = "usage: %s [OPTIONS] arguments %s "% (sys.argv[0], getopt)

  try:
      (opts, args) = getopt.parse(sys.argv[1:])
  except Exception, inst:
      print inst
      print usage; sys.exit(1)

  keys = opts.keys()

  # not typical use of parsed arguments and options perhaps
  
  if('-h' in keys):
      print "option -h was set:", opts['-h']  # opts['--help'] produces same result

  if('-v' in keys):            
      print "option -v was set:", opts['-v']
                               
  if('-d' in keys):            
      print "option -d was set:", opts['-d']
                               
  if('-f' in keys):            
      print "option -f was set:", opts['-f']
                               
  if('-a' in keys):            
      print "option -a was set:", opts['-a']
                               
  if('-I' in keys):            
      print "option -I was set:", opts['-I']


  # remaining arguments 

  print "args ", args


"""
# TODO: split short bool opts placed together (-abcde --> -a -b -c -d -e)


__author__  = "bjarneh@ifi.uio.no"
__version__ = "1.1"



class Option:
    """
    Option

    super class for the StringOption and BoolOption
    the functions and elements they have in common are placed
    in this class. this way we can avoid some of the
    isinstance - checking later on..
    """
    def __init__(self, opts):

        if(type(opts) in (str,)):
            self.opts = [opts]
        elif(type(opts) in (list,)):
            self.opts = [ str(o) for o in opts ]

    def contains(self, opt):
        """ tells wheter an option can be found in this Option object """
        if(opt in self.opts):
            return 1
        else:
            return 0
     

#__________________________________________________________________________________#


class StringOption(Option):
    """
    StringOption

    this class holds options which are not only switches (on/off)
    but require trailing arguments. an exception is raised if the
    number of trailing arguments differ from what it should be.
    there is also the possibility to test each trailing argument 
    by providing a  function which returns a boolean result pending
    on the whether the argument fulfilled the requirements.

    example:

    test_func = lambda x : re.match(r'^[0-9]+$', x)

    sending this as the test func will make sure that all options
    are actually natural numbers (or else an exception is raised).
    """

    def __init__(self, opts, trailing=1, default=[], test=None, errormsg=None):
        Option.__init__(self, opts)
    
        self.trailing = trailing
        self.default = default
        self.test = test
        self.values = []
        self.errormsg = errormsg

    def test_arg(self, arg):
        """ 
        if there is given a test function trailing arguments will
        be tested against it, should any of them fail an exception is
        raised
        return -> Boolean
        """
        return ((not self.test) or self.test(arg))

    def add_value(self, v):
        """ add a trailing argument to this option"""
        self.values.append(v)
    
    def get_value(self):
        """ return trailing arguments"""
        return self.values

    def is_set(self):
        """ tell's whether or not an option was given as an input argument """
        return (self.values != self.default)

        
#__________________________________________________________________________________#


class BoolOption(Option):
    """
    BoolOption

    this class represents the options that do not
    take any trailing arguments, but are only switches
    that can be turned on
    """
    def __init__(self, opts):
        Option.__init__(self, opts)
        self.set = 0
    
    def set_it(self):
        """ sets boolean argument, which means  """
        self.set = 1

    def get_value(self):
        """ returns value for BoolOption (True/False) """
        return self.set

    def is_set(self):
        """ tells whether or not this option was set """
        return self.set


#__________________________________________________________________________________#



class GetOpt:
    """
    GetOpt

    this class parses the input arguments and inserts the
    arguments into the option classes where they belong.
    """

    def __init__(self,opts=None):
        
        self.remain = []
        self.opts = []

        if(opts):
            self.add(opts)


    def add(self, opts):
        """ add option or list of options to GetOpt """
        if(type(opts) in (list,)):
            for elm in opts:
                if(not isinstance(elm, (StringOption, BoolOption))):
                    raise Exception("StringOption or BoolOption required")
            self.opts += opts
        else:
            if(not isinstance(opts, (StringOption, BoolOption))):
                raise Exception("StringOption or BoolOption required")
            self.opts.append(opts)


    def add_bool_option(self, opts):
        """ initialize and add a BoolOption to GetOpt """
        b_opt = BoolOption(opts)
        self.add(b_opt)       


    def add_str_option(self, opts, trailing=1, default=[], test=None, errormsg=None):
        """ initializa and add a StringOption to GetOpt """ 
        s_opt = StringOption(opts, trailing=trailing, default=default, test=test, errormsg=errormsg)
        self.add(s_opt)


    def preprocess(self, args):
        """
        this function seperates options from arguments
        if they are written as one word (--file=somefile)
        given that the '--file=' option requires an argument
        if not they are left as is.
        return -> list of arguments where some may have been split up
        
        preprocess(['-o', 'something', '-I/usr/lib']) -> ['-o', 'something', '-I', '/usr/lib']
        
        if '-I' is an option which takes an argument 
        """

        real_args = []
        s_opts = []
        cmp_func = lambda x, y : len(x) < len(y) or -1
        

        for i in self.opts:
            if(isinstance(i, StringOption)):
                s_opts += i.opts

    
        for arg in args:
            
            possible_opts = []

            for so in s_opts:
                if(arg.startswith(so)):
                    possible_opts.append(so)
            
            if(possible_opts):
                if(len(possible_opts) > 1):
                    possible_opts.sort(cmp_func)

                option = possible_opts[0]
                real_args.append(arg[0:len(option)])
                real_args.append(arg[len(option):])

            else:
                real_args.append(arg)

        return [ o.strip() for o in real_args if o.strip() != ""]



    def parse(self, args):
        real_args = self.preprocess(args)

        while(real_args):
            arg = real_args.pop(0)
            possible_opt = self.is_option(arg)
            if(possible_opt and isinstance(possible_opt, BoolOption)):
                # if boolean just pop and set
                possible_opt.set_it()
            elif(possible_opt and isinstance(possible_opt, StringOption)):
                # strip and check
                if(possible_opt.trailing > 0):
                    for elm in range(0, possible_opt.trailing):
                        if(real_args):
                            possible_arg = real_args[0]
                            if(self.is_option(possible_arg)):
                                raise Exception("got option '"+str(possible_arg)+"' expected argument")
                            elif(possible_opt.test_arg(possible_arg)):
                                real_args.pop(0) # pop argument of arg-list
                                possible_opt.add_value(possible_arg)
                            else:
                                if(possible_opt.errormsg):
                                    msg = possible_opt.errormsg
                                else:
                                    msg = "argument '"+str(possible_arg)+"' failed argument test for option '"+str(arg)+"'"
                                raise Exception(msg)
                        else:
                            raise Exception("option: "+str(arg)+
                                            " (requires "+str(possible_opt.trailing)+" arguments)")
                
                else:
                    while(real_args):
                        possible_arg = real_args[0]
                        # horrible test, but needed to ensure traling
                        # arguments which are also actual options
                        if( not  (self.is_option(possible_arg) and
                                  possible_opt.get_value() ) and
                           possible_opt.test_arg(possible_arg) ):
                            possible_opt.add_value(possible_arg)
                            real_args.pop(0)
                        else:
                            break


            else:
                self.remain.append(arg)

        return (self.gen_xdict(), self.remain)


    def gen_xdict(self):
        """ 
        this function generates an 'extended' dictionary from
        the options, the xdict class has some overloaded functions to
        ease the fetching, and locating of elements.
        """
        h = xdict()
        for o in self.opts:
            if(o.is_set()):
                h[tuple(o.opts)] = o.get_value()
        return h


    def is_option(self, arg):
        """ tells whether some argument is an option """
        for opt in self.opts:
            if(opt.contains(arg)):
                return opt
        return None


    def __str__(self):
        """ formats the options for pretty printing of all options """
        r_str = "\n\noptions:\n\n"
        
        if(not self.opts): return ""
        for op in self.opts:
            r_str += "+  [ "+"   ".join(op.opts) +" ]\n"
        return r_str


#__________________________________________________________________________________#

class xdict(dict):
    """

    this class extends the regular dictionary with a few
    facilities, which makes it easy to fetch an item even though
    its keys are tuples.
    example:

    h[('-v', '--version')] = 1

    can be a typical entry, but since __getitem__ is overloaded
    these can be fetched using:

    h['-v']

    or

    h['--version']

    also the dict.keys() function has been overloaded
    """
    def __init__(self):
        dict.__init__(self)
    
    def keys(self):
        """ 
        return list of 'all' keys, since keys can be tuples 
        something has to be done in order to get all of them
        returned as one list.
        """
        super_keys = dict.keys(self)
        my_keys = []
        for keys in super_keys:
            my_keys += list(keys)

        return my_keys

    def __getitem__(self, k):
        """ return an element if it is part of a tuple-key """
        if(k in self.keys()):
            for keys in dict.keys(self):
                if(k in keys):
                    return dict.__getitem__(self,keys)
        else:
            raise KeyError(str(k))



if __name__ == '__main__':
   
    import sys, re, os
    
    getopt = GetOpt()

    getopt.add_bool_option(['-h', '-help', '--help', '?'])
    getopt.add_bool_option(['-v', '-version', '--version'])
    getopt.add_str_option(['-s', '-span', '--span'], trailing=2, test = lambda x : re.match(r'^\d+$', x))
    getopt.add_str_option(['-f', '-f=', '-file', '-file=', '--file', '--file='],
                          test=lambda x : os.path.isfile(x), errormsg="argument to '-file' must be"+
                          " a valid filename")
    getopt.add_str_option(['-d', '-d=', '-dir', '-dir=', '--dir', '--dir='],  test=lambda x : os.path.isdir(x))

    # add option which can occur multiple times -I/some/lib -I/some/other/lib
    getopt.add_str_option('-I', trailing=-1 )

    usage = "\nusage: %s [OPTIONS] arguments %s "% (sys.argv[0], getopt)

    try:
        (opts, args) = getopt.parse(sys.argv[1:])
    except Exception, inst:
        print inst
        print usage; sys.exit(1)

    keys = opts.keys()

    if('-h' in keys):
        print "option -h was set:", opts['-h']
                                 
    if('-v' in keys):            
        print "option -v was set:", opts['-v']
                                 
    if('-d' in keys):            
        print "option -d was set:", opts['-d']
                                 
    if('-f' in keys):            
        print "option -f was set:", opts['-f']
                                 
    if('-a' in keys):            
        print "option -a was set:", opts['-a']
                                 
    if('-I' in keys):            
        print "option -I was set:", opts['-I']

    if('-s' in keys):
        print "option -s was set:", opts['-s']

    print "args ", args
