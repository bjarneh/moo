#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.uio.ifi.bjarneh.cl.parse.Parser

A simple Prolog parser for the geometric logic
grammer used by geolog.
"""

import sys
from inspect import currentframe
from Lexer import Lexer


__author__='bjarneh@ifi.uio.no'
__version__='Parser.py 0.1'


def lineNo(curframe):
    """ utility function to help me find out
    where things are failing, without cluttering
    up large parts of the code"""
    return "\n[ Parser.py  line: "+str(curframe.f_lineno)+" ]"


class Parser(object):
    """
    Parser
    tries to parse a file based on the Prolog syntax used by
    Marc Bezem's coherent logic prover. The resulting tree
    is able to assemble a set of rewrite rules (Maude) which 
    will be used to build another theorem-prover.
    """

    def __init__(self, filename=None):
        self.tokenizer = None
        if(filename): 
            self.tokenizer = self.getTokens(filename)

    def getTokens(self, filename):
        """ lex file and return list of tokens (tokenizer) """
        lexer = Lexer()
        try:
            tokenizer = lexer.fileScan(filename)
        except Exception, inst:
            sys.stderr.write(str(inst)+'\n')
            sys.exit(1)
        return tokenizer

    def perror(self, msg):
        """
        print an error message and quit, this will
        be called when we get an unexpected end of tokens,
        or a sequence of characters which does not match our
        grammar/syntax.
        """
        sys.stderr.write(str(msg)+'\n')
        sys.stderr.write(self.tokenizer.where())
        sys.exit(1)
    
    def skipExpectedToken(self, token=None, ttype=None, msg=""):
        """ see if next token is as expected, if not write error message
        and quit, for now this is very basic and the user gets very
        bad info on what exactly went wrong and where..."""
        
        if(not (token or ttype) ): 
            raise Exception("Parser.skipExpectedToken: token or ttype required")

        curToken = self.tokenizer.current()

        if(ttype):
            if(not curToken):
                self.perror(msg+" unexpected end of tokens")
            elif(curToken.ttype != ttype):
                self.perror(msg+" expected type: "+ttype+", got: "+curToken.ttype)

        elif(token):
            if(not curToken):
                self.perror(msg+" unexpected end of tokens")
            elif(curToken != token):
                self.perror(msg+" expected token '"+token+"' got '"+
                            curToken.tvalue+"'")

        self.tokenizer.readnext()

        return curToken


    
    def parseTheory(self, filename=None):
        """
        syntax: axiomList
        """
        if(filename):
            self.tokenizer = self.getTokens(filename)
        else:
            self.perror(lineNo(currentframe())+ 
                        "  need something to parse")

        theory = Theory()

        if(not self.tokenizer.current()):
            self.perror(lineNo(currentframe())+ 
                        "  unexpected end of tokens ")

        # parse axioms as long as there are tokens
        while(self.tokenizer.current()):
            theory.append(self.parseAxiom())

        return theory




    def parseAxiom(self):
        """syntax: L-Formula => R-Formula . """
       
        left = self.parseLeftAxiom()

        self.skipExpectedToken(token='=>',msg=lineNo(currentframe()))

        right = self.parseRightAxiom()

        self.skipExpectedToken(token='.', msg=lineNo(currentframe()))

        return Axiom(left, right)


    def parseRightAxiom(self):
        """ predicateList | goal | false """

        tok = self.tokenizer
        curToken = tok.current()

        if(not curToken):
            self.perror(lineNo(currentframe())+" unexpected end of tokens ")

        if(curToken.ttype != 'WORD'):
            self.perror(lineNo(currentframe())+" expected token of type 'WORD' got' "
                        +str(curToken.ttype)+"'")

        if(curToken.tvalue in ['false','goal']):
            tok.readnext()
            return SpecialFormula(curToken.tvalue)
        else:
            formula = Formula()
            formula.append(self.parsePredicate())
            while(1):
                if(not tok.current()):
                    self.perror(lineNo(currentframe())+" unexpected end of tokens")
                    break
                elif(tok.current().tvalue in [',', ';']):
                    formula.append(tok.current().tvalue)
                    tok.readnext()
                    formula.append(self.parsePredicate())
                elif(tok.current() == '.'):
                    break
                else:
                    self.perror(lineNo(currentframe())+" expected ',' or '.'  got '"+
                                tok.current().tvalue+"'")
                    break

        return formula



    def parseLeftAxiom(self):
        """ predicateList | true """

        tok = self.tokenizer

        if(not tok.current()):
            self.perror(lineNo(currentframe())+" unexpected end of tokens ")

        if(tok.current().ttype != 'WORD'):
            self.perror(lineNo(currentframe())+" expected token of type 'WORD' got' "
                        +str(tok.current().ttype)+"'")

        if(tok.current() == 'true'):
            tok.readnext()
            return SpecialFormula('true')
        else:
            formula = Formula()
            formula.append(self.parsePredicate())
            while(1):
                if(not tok.current()):
                    self.perror(lineNo(currentframe())+" unexpected end of tokens")
                    break
                elif(tok.current() == ','):
                    # these are always separated by ',' so no need to store
                    # the logical separator since formulas are geometric
                    tok.readnext()
                    formula.append(self.parsePredicate())
                elif(tok.current() == '=>'):
                    break
                else:
                    self.perror(lineNo(currentframe())+" expected ',' or '=>'  got '"+
                                tok.current().tvalue+"'")
                    break

        return formula


    def parsePredicate(self):
        """ predicate:  'WORD' '(' TERMLIST ')' """

        name = self.skipExpectedToken(ttype='WORD',
                                      msg=lineNo(currentframe()))
        predicate = Predicate(name.tvalue)
        self.skipExpectedToken(token='(', msg=lineNo(currentframe()))
        
        # termlist is added to predicate
        predicate.addTermList(self.parseTermList())
        self.skipExpectedToken(token=')', msg=lineNo(currentframe()))

        return predicate

    
    def parseTermList(self):
        """ termlist: term, term, term,... """

        termlist = TermList()
        termlist.append(self.parseTerm())

        while(self.tokenizer.current() == ','):
            self.skipExpectedToken(token=',')
            termlist.append(self.parseTerm())

        return termlist
        

    def parseTerm(self):
        """ term : 'VARIABLE' | 'WORD' """

        curToken = self.tokenizer.current()

        if(not curToken):
            self.perror(lineNo(currentframe())+" unexpected end of tokens")

        if(not curToken.ttype in ['VARIABLE', 'WORD']):
            self.perror(lineNo(currentframe())+" term must be of type 'VARIABLE' or "+
                        "'WORD' not '"+curToken.ttype+"'")

        self.tokenizer.readnext()

        return Term(curToken.tvalue, curToken.ttype)

        

#______________________________________________________________________________

class Theory(list):
    """
    Theory holds a list of Axioms
    """
    def __init__(self):
        self.maxConstant = 1

    def printInfo(self):
        for ax in self:
            print "goalAxiom", ax.goalAxiom()
            print "factAxiom", ax.factAxiom()
            print ax

    def getPredicates(self):
        """ we gather all predicates to fill template (Maude module)"""
        preds = []
        for ax in self:
            ax.addPredicates(preds)
        return preds

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join(map(str, self))

    def toRuleRepresentation(self):
        """ 
        before we have inserted natural numbers for
        constants, and converted fresh variables in the 
        right hand side of rules this will not work.
        so this is done prior to the actual conversion
        """

        # insert natural numbers for constants
        nd = natdict()
        for ax in self:
            ax.constants2nats(nd)

        # this will tell us how big the next 'fresh' constants is
        self.maxConstant = max(nd.values()) + 1

        # convert fresh variables in the rhs to negative ints
        for ax in self:
            ax.fresh2int()

        # here we start with the actual conversion
        rules = []
        rulecount = 1
        rules.append("--- rewrite rules start")
        for ax in self:
            rules.append(ax.toRuleRepresentation(rulecount))
            rulecount += 1
        rules.append("--- rewrite rules done")
        return "\n".join(rules)
        

    def getFacts(self):
        facts = []
        for ax in self:
            if ax.factAxiom():
                ax.addFacts(facts)
        return ', '.join(facts)

#______________________________________________________________________________

class Axiom(object):
    """
    Axiom  Formula => Formula
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def getRight(self):
        """ return list containing only Predicates"""
        return [ a for a in self.right if a != ',' and a != ';' ]

    def goalAxiom(self):
        """ true if axiom ends with conclusion 'goal' or 'false'"""
        if(type(self.right) in (SpecialFormula,)):
            return 1
        else:
            return 0

    def addFacts(self, facts):
        self.right.addFacts(facts)

    def factAxiom(self):
        """ true if axiom starts with antecedent 'true' """
        if(type(self.left) in (SpecialFormula,)):
            return 1
        else:
            return 0

    def fresh2int(self):
        if not (self.goalAxiom() or self.factAxiom()):
            leftVariables = []
            self.left.insertLeftVariables(leftVariables)
            nd = natdict()
            self.right.findFreshVariables(leftVariables, nd)
            self.right.insertRightVariables(nd)

    def constants2nats(self, natconst):
        if type(self.left) not in (SpecialFormula,):
            for f1 in self.left:
                f1.constants2nats(natconst)
        if type(self.right) not in (SpecialFormula,):
            for f2 in self.right:
                if f2 not in [',',';']:
                    f2.constants2nats(natconst)
    
    def addPredicates(self, preds):
        """ add predicates to list preds """
        self.left.addPredicates(preds)
        self.right.addPredicates(preds)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.left.__str__() + " => " + self.right.__str__()

    def toRuleRepresentation(self, count):
        if not self.factAxiom():
            rule = []
            rule.append('rl [ rule%d ]: '%(count))
            rule.append(self.left.toRuleRepresentation(1))
            rule.append(' => ')
            rule.append(self.right.toRuleRepresentation(0))
            rule.append(' . ')
            return ''.join(rule)
        return '---[ rule%d ]   removed because it was a fact-rule'%(count)

#______________________________________________________________________________

class Formula(list):
    """
    Formula
    a list of Predicates separated by , or ;
    """
    def __init__(self):
        pass

    def addPredicates(self, preds):
        """ add all predicates not alredy in preds"""
        for predicate in self:
            if predicate not in preds and predicate not in [',',';']:
                preds.append( predicate )

    def constants2nats(self, natconst):
        for predicate in self:
            if predicate not in [',',';']:
                predicate.constants2nats(natconst)

    def toRuleRepresentation(self, leftside):
        formularep = []
        for predicate in self:
            if predicate in [',',';']:
                formularep.append(predicate)
            else:
                formularep.append(predicate.toRuleRepresentation())
        if leftside:
            return ', '.join(formularep)
        else:
            return ' '.join(formularep)


    def insertLeftVariables(self, leftvars):
        for predicate in self:
            predicate.insertLeftVariables(leftvars)

    def findFreshVariables(self, leftvars, ndict):
        for predicate in self:
            if predicate not in [',',';']:
                predicate.findFreshVariables(leftvars, ndict)

    def insertRightVariables(self, ndict):
        for predicate in self:
            if predicate not in [',',';']:
                predicate.insertRightVariables(ndict)

    def addFacts(self, facts):
        for predicate in self:
            if predicate not in [',',';']:
                facts.append(predicate.toRuleRepresentation())

#______________________________________________________________________________

class SpecialFormula(object):
    """
    SpecialFormula
    represent formula's which consist of a single
    constant, limited to: true, false, goal
    """
    def __init__(self, constant):
        self.constant = constant

    def __str__(self):
        return str(self.constant)

    def addPredicates(self, preds):
        """ 
        just add this here to make SpecialFormula
        seem like a regular Formula as far as adding
        predicates go
        """
        pass

    def constants2nats(self, natconst):
        """ 
        just add this here to make SpecialFormula
        seem like a regular Formula as far as converting
        constants to natural numbers
        """
        pass

    def toRuleRepresentation(self, leftside):
        """ goal -> Goal, false -> False, true -> True"""
        return self.constant.capitalize()
#______________________________________________________________________________

class Predicate(object):
    """
    Predicate
    a name followed by a list of Terms
    """
    def __init__(self, name):
        self.name = name
        self.termlist = None

    def addTermList(self, tl):
        self.termlist = tl

    def getName(self):
        return self.name

    def __eq__(self, other):
        if type(other) in (Predicate,):
            if other.getName() == self.getName():
                if other.__len__() == self.__len__():
                    return 1
        return 0

    def insertLeftVariables(self, leftvars):
        for t in self.termlist:
            t.insertLeftVariables(leftvars)

    def findFreshVariables(self, leftvars, ndict):
        for t in self.termlist:
            t.findFreshVariables(leftvars, ndict)

    def insertRightVariables(self, ndict):
        for t in self.termlist:
            t.insertRightVariables(ndict)

    def __deepcopy__(self, orefs):
        """ 
        create a fake deepcopy of predicates, fake in the
        sense that we fill all predicates with variables,
        unique variables.
        """
        p = Predicate(self.name)
        cnt = 1
        fakeTermList = []
        for i in range(0, self.__len__()):
            fakeTermList.append("X%d:Int"%(cnt))
            cnt += 1
        p.addTermList(fakeTermList)
        return p


    def __len__(self):
        return self.termlist.__len__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.name) + str(self.termlist) 

    def constants2nats(self, natconst):
        for t in self.termlist:
            t.constants2nats(natconst)

    def toRuleRepresentation(self):
        prep = []
        prep.append(" %s( "%(self.name))
        prep.append(self.termlist.toRuleRepresentation())
        prep.append(" ) ")
        return ''.join(prep)


#______________________________________________________________________________

class TermList(list):
    """
    TermList
    a comma separated list of Terms
    """
    def __init__(self):
        pass

    def toRuleRepresentation(self):
        terms = []
        for t in self:
            terms.append(t.toRuleRepresentation())
        return ', '.join(terms)
#______________________________________________________________________________

class Term(object):
    """
    Term
    a variable or constant
    """
    def __init__(self, tvalue, ttype):
        self.tvalue = tvalue
        self.ttype = ttype
        self.mtype = None

    def constants2nats(self, natconst):
        if self.ttype == 'WORD':
            natconst.addConstant(self.tvalue)
            self.mtype = str(natconst[self.tvalue])
        else:
            self.mtype = self.tvalue + ":Int"

    def insertLeftVariables(self, leftvars):
        if self.ttype == 'VARIABLE':
            if self.tvalue not in leftvars:
                leftvars.append(self.tvalue)

    def findFreshVariables(self, leftvars, ndict):
        if self.ttype == 'VARIABLE':
            if self.tvalue not in leftvars:
                ndict.addConstant(self.tvalue)

    def insertRightVariables(self, ndict):
        if self.ttype == 'VARIABLE':
            if ndict.has_key(self.tvalue):
                self.mtype = str( (-1 * ndict[self.tvalue]) )

    def toRuleRepresentation(self):
        return self.mtype

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.tvalue)
#______________________________________________________________________________


class natdict(dict):
    """
    a small class which just wraps a dictionary
    to get a mapping from constants to natural numbers
    so constants: a,b,c,d,e -> 1,2,3,4,5 
    """
    def __init__(self):
        dict.__init__(self)
        self.counter = 1

    def addConstant(self, constant):
        if not constant in self.keys():
            self[constant] = self.counter
            self.counter += 1

#______________________________________________________________________________

if __name__ == '__main__':
    pass
