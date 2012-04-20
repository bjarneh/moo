#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.uio.ifi.bjarne.cl.parse.Lexer

A small Lexer for the Prolog grammar used
by Marc Bezem and John Fishers Geolog prover
"""

import sys, re

__author__='bjarneh@ifi.uio.no'
__version__='Lexer.py 0.1'

class Lexer(object):
    """
    Lexer
    using the regular expressions given to the re.Scanner class
    pieces of string is returned and given to callbacks (functions).
    for each callback (unless it is set to None) we initializes a 
    Token object, which is then returned to the scanner, who assembles
    these into a list. That list is then put into a class called Tokenizer 
    which hands them out one Token at a time.
    """

    def __init__(self):
        self.scanner = re.Scanner(self.prologGrammar())

    def __iter__(self):
        return self.scanner.__iter__()

    def prologGrammar(self):
        grammar = []
        grammar.append( (r"[a-z][a-zA-Z0-9_]*", self.word) )
        grammar.append( (r"[A-Z_][a-zA-Z0-9_]*", self.variableident) )
        grammar.append( (r",|;|=>", self.logisep) ) 
        grammar.append( (r"\.", self.endprolog) )
        grammar.append( (r"\(", self.startprnt) )
        grammar.append( (r"\)", self.endprnt) )
        grammar.append( (r"%.*\n", None) ) # ignore comments
        grammar.append( (r"\s*", None) ) # ignore whitespace
        return grammar

    
    def fileScan(self, fname):

        if(fname == '-'):
            lines = sys.stdin.read()
        else:
            fh = open(fname, 'r')
            lines = fh.read()
            fh.close

        return self.scan(lines)


    def scan(self, input):
        tokens, remainder = self.scanner.scan(input)
        if(remainder):
            sys.stderr.write("[ warning ] entire file did not match grammar \n")
        return Tokenizer(tokens)

    ## the actual tokens returned

    def variableident(self, scanner, token):
        return Token('VARIABLE', token)

    def logisep(self, scanner, token):
        return Token('LOGICSEPARATOR', token)

    def word(self, scanner, token):
        return Token('WORD', token)

    def startprnt(self, scanner, token):
        return Token('STARTPARENTHESIS', token)

    def endprnt(self, scanner, token):
        return Token('ENDPARENTHESIS', token)

    def endprolog(self, scanner, token):
        return Token('ENDPROLOG', token)


#______________________________________________________________________________

class Tokenizer(object):
    """
    Tokenizer
    returns tokens one at a time, and will also stuff
    used tokens into self.buffer. this can be useful
    when something goes wrong during parsing to inform
    user of where in the text he has syntax errors.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.buffer = []

    def current(self):
        if(self.tokens): return self.tokens[0]
        return None

    def readnext(self):
        self.buffer.append(self.tokens[0].tvalue)
        del self.tokens[0]

    def hasmore(self):
        return self.tokens

    def unshift(self, token):
        self.tokens.insert(0, token)

    def where(self):
        """ report where in file error occured"""
        
        if(not self.buffer): return "\n"

        for i in range(0, len(self.buffer)):
            if(self.buffer[i] == '.'):
                self.buffer[i] = '.\n'

        errbuffer = ''.join(self.buffer)

        i = len(errbuffer) -1
        while(errbuffer[i] != '\n' and i > 0):
            i = i -1
        placement = '\n'+ ' '* (len(errbuffer) - i -1) + '^^^'
        
        return "\n\n"+errbuffer+placement+'\n\n'

    def __str__(self):
        return self.tokens.__str__()

#______________________________________________________________________________

class Token(object):
    """
    Token
    represents a single token, contains
    value and type, '==' is overloaded to
    compare with value.
    """
    
    def __init__(self, t_type, t_value):
        self.ttype = t_type
        self.tvalue = t_value

    def __eq__(self, other):
        """ equality testing is based on token, not type"""
        return str(self.tvalue) == str(other)

    def __ne__(self, other):
        """ equality testing is based on token, not type"""
        return not self.__eq__(other)

    def __str__(self):
        s_token = []
        s_token.append('Token(')
        s_token.append(str(self.ttype)+", ")
        s_token.append("'" + str(self.tvalue) + "')")
        return ''.join(s_token)

#______________________________________________________________________________

if __name__ == '__main__':
    
    testinput = """

    true => exists(a), exists(b), exists(c). %1  

    re(b,X), re(c,X) => goal. %2     

    exists(X) => e(X,X). %3                  

    true => re(a,b), re(a,c). %4  

    e(X,Y) => e(Y,X).  %5

    e(X,Y), re(Y,Z) => re(X,Z). %6

    e(X,Y) => re(X,Y). %7                

    r(X,Y) => re(X,Y). %8              

    re(X,Y) => e(X,Y) ; r(X,Y). %9

    r(X,Y), r(X,Z) => exists(U), r(Y,U), r(Z,U). %10

    """
    lexer = Lexer()
    if(len(sys.argv) <= 1):
        tokenizer = lexer.scan(testinput)
    else:
        tokenizer = lexer.fileScan(sys.argv[1])

    while(tokenizer.hasmore()):
        print tokenizer.current()
        tokenizer.readnext()
