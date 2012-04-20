#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.ifi.uio.bjarneh.cl.template.filler

This file holds a class able to create fill for the template which then turns
into a Maude module. This is what will be filled by this class:


1. predicate definitions (definition) [ yepp ]
2. refresh definitions   (function)   [ yepp ]
3. maximum definitions   (function)   [ yepp ]
4. v2z definitions       (function)   [ yepp ]
5. helpex definitions    (function)   [ yepp ]
6. possible comment to remove print statement        [ nope ]
7. actual term to rewrite in order to prover formula [ nope ]

"""

import copy
from no.uio.ifi.bjarneh.cl.template.monologuetemplate import MaudeTemplate

__author__='bjarneh@ifi.uio.no'
__version__='filler.py 0.1'


class Filler(object):
    def __init__(self, theory):
        self.theory = theory
        preds = theory.getPredicates()
        self.preds = copy.deepcopy(preds)

    def surround(self, start, end, elmt):
        return start + str(elmt) + end

    def getOpDecl(self):
        """ return operator declarations for Maude module"""
        opdecls = ["--- operator declarations start"]
        for pred in self.preds:
            opdecls.append("op %s : %s -> Fact ."%(pred.name,'Int '*len(pred)))
        opdecls.append("--- operator declarations done")
        return '\n'.join(opdecls)

    def getRefresh(self):
        """ return refresh equations for Maude module"""
        refreshdecls = ["--- refresh declarations start"]
        for pred in self.preds:
            name = pred.name
            vars = ', '.join( pred.termlist )
            surroundedvars = [ self.surround('refresh(N1, ',')', a) for a in pred.termlist]
            refreshdecls.append("eq refresh(N1, %s( %s )) = %s( %s ) ."
                                %(name,vars,name,', '.join(surroundedvars)))
        refreshdecls.append("--- refresh declarations done")
        return '\n'.join(refreshdecls)
                

    def getMaximum(self):
        """ return maximum equations for Maude module"""
        maximumdecls = ["--- maximum declarations start"]
        for pred in self.preds:
            name = pred.name
            vars = ', '.join( pred.termlist )
            maxstart = "eq maximum( %s(%s) ) = "%(name,vars)
            if(len(pred) > 1):
                maxend = " max(%s) ."%(vars)
            else:
                maxend = "%s ."%(vars)
            maximumdecls.append(maxstart + maxend)
        maximumdecls.append("--- maximum declarations done")
        return '\n'.join(maximumdecls)


    def getv2z(self):
        """ return v2z (variable 2 zero) equations for Maude module"""
        v2zdecls = ["--- v2z declarations start"]
        for pred in self.preds:
            name = pred.name
            vars = ', '.join( pred.termlist )
            surroundedvars = [ self.surround('v2z(',')', a) for a in pred.termlist]
            v2zdecls.append("eq v2z( %s( %s )) = %s( %s ) ."
                                %(name,vars,name,', '.join(surroundedvars)))
        v2zdecls.append("--- v2z declarations done")
        return '\n'.join(v2zdecls)

    def getHelpex(self):
        """ return helpex equations for Maude module"""
        helpexdecls = ["--- helpex declarations start"]
        for pred in self.preds:
            name = pred.name
            vars = ', '.join( pred.termlist )
            surroundedvars = [ self.surround('helpex(',')', a) for a in pred.termlist]
            helpexdecls.append("eq helpex( %s( %s ) ) =  %s  ."
                                %(name,vars,' or '.join(surroundedvars)))
        helpexdecls.append("--- helpex declarations done")
        return '\n'.join(helpexdecls)

    def getRules(self):
        """ return the object level rewrite rules that corresponds
        to the input formula parsed in advance"""
        return self.theory.toRuleRepresentation()

    def getFacts(self):
        """ return right hand side of all rules that have a
        left hand which is equal to 'true'"""
        return self.theory.getFacts()

    def getMaudeModule(self, depth, printOn):
        """ using the othe equations in this class we are now
        able to fill all the functions and rewrite rules of the
        template, we also fill in depth from user which states
        how many iterations we would like to do on a single branch
        before we give up, the printOn variable will either turn
        print statement on, or not"""
        return MaudeTemplate%(self.getOpDecl(),
                             self.getRefresh(),
                             self.getMaximum(),
                             self.getv2z(),
                             self.getHelpex(),
                             self.getRules(),
                             printOn,
                             self.getFacts(),
                             self.theory.maxConstant) #depth

if __name__ == '__main__':
    pass
