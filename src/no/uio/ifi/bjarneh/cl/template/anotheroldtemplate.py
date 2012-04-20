#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
no.ifi.uio.bjarneh.cl.template.monologuetemplate

this file holds the Monologue template (Maude code),
which is the rewrite theory needed in order to prove
things, plus some placeholders which will be filled
with content based on what we are trying to prove.

the content that needs to be filled:

1. predicate definitions        (definition)
2. refresh definitions          (equation)
3. maximum definitions          (equation)
4. v2z definitions              (equation)
5. helpex definitions           (equation)
6. GeoTheory rewrite rules      (rewrite rules)
7. possible comment to remove print statement
8. actual term to rewrite in order to prover formula

"""

__author__='bjarneh@ifi.uio.no'
__version__='monologuetemplate.py 0.1'

MaudeTemplate="""
---- This is an attempt at making a rewrite theory able to
---- prove formulas in geometric logic, or coherent logic.
---- 
---- There are lots of cases which are not taken care of
---- by these rewrite theories, i.e., all terms of a specific
---- sort will not match most equations. This is perhaps 
---- a not good in most situations, but here it most certainly
---- is, since it's used for debugging (more or less).
---- I.e., it's usually much better to get a large term
---- which the equations are unable to parse, then to get
---- some sort of wierd result in the end, having no clue as
---- to where it all went wrong.

---- Also want to mention that Maude has gone from being the
---- only language more difficult to debug than assembler,
---- to one of the simplest on the planet. Naturally all that
---- was required was some sort of printf statement, which
---- it now has.


fmod GeoTerm is

protecting INT .
protecting META-LEVEL .

sort Fact .
sort FactSet .
sort Disjoint .
subsort Fact < FactSet .
subsort FactSet < Disjoint .


op Goal  : -> Disjoint .
op False : -> Disjoint .

--- start compile time
%s
--- end compile time
           
op _;_     : Disjoint Disjoint -> Disjoint [ assoc prec 47 format(d y o d) ] .
op _,_     : FactSet FactSet -> FactSet [ comm assoc prec 45 ] .

op refresh : Nat Disjoint -> Disjoint .
op refresh : Nat Int -> Nat .
op maximum : Disjoint -> Nat .
op remax   : Disjoint -> Nat .
op v2z     : Disjoint -> Disjoint .  --- var to zero
op v2z     : Int -> Int .
op helpex  : Disjoint -> Bool .
op helpex  : Int -> Bool .
op exrule  : Disjoint -> Bool .


vars F1 F2 F3    : Fact .
vars FS1 FS2     : FactSet .
vars N1 N2       : Nat .

--- make a set out of these facts
eq F1, F1 = F1 .


eq refresh(N1, FS1 ; FS2) = refresh(N1, FS1) ; refresh(N1, FS2) .
eq refresh(N1, FS1, FS2) = refresh(N1, FS1), refresh(N1, FS2) .
eq refresh(N1, Goal) = Goal .
eq refresh(N1, False) = False .

eq refresh(N1, I1:NzInt) = N1 + abs(I1:NzInt) .
eq refresh(N1, I1:Int) = I1:Int [owise] .


--- start compile time
%s
--- end compile time


eq maximum(FS1 ; FS2) = max( maximum(FS1) , maximum(FS2) ) .
eq maximum(FS1, FS2) = max( maximum(FS1), maximum(FS2) ) .
eq maximum(Goal) = 0 .
eq maximum(False) = 0 .

--- start compile time
%s
--- end compile time

--- @see v2z
eq remax(D:Disjoint) = maximum( v2z(D:Disjoint) ) .

--- the function v2z stands for variable 2 zero,
--- it is used before we calculate the maximum
--- variable of a factset, this is how it is used:
---
--- v2z( p(X:Int, 1) , r(Y:Int, 3) ) == p(0,1), r(0,3)
--- 
--- now our term is a ground term without variables
--- and a simple call to maximum will result in the
--- natural number 3, this is what the function
--- 'remax' does

eq v2z(FS1 ; FS2) = v2z(FS1) ; v2z(FS2) .
eq v2z(FS1 , FS2) = v2z(FS1) , v2z(FS2) .
eq v2z(Goal) = Goal .
eq v2z(False) = False .

--- start compile time
%s
--- end compile time

eq v2z(I1:Int) = 
    if ( upTerm(I1:Int) :: Variable ) then 
        0
    else
        I1:Int
    fi .

eq exrule(D:Disjoint) = helpex( v2z(D:Disjoint) ) .

eq helpex(FS1 ; FS2) = helpex(FS1) or helpex(FS2) .
eq helpex(FS1 , FS2) = helpex(FS1) or helpex(FS2) .
eq helpex(Goal) = false .
eq helpex(False) = false .

--- start compile time
%s
--- end compile time

ceq helpex(I1:Int) = true if ( I1:Int < 0 ) .
eq  helpex(I1:Int) = false [owise] .

endfm



mod GeoTheory is

protecting META-LEVEL .
protecting GeoTerm .

vars X Y Z U : Int .

--- start compile time
%s
--- end compile time

endm


mod SetRewrite is

protecting GeoTheory .
protecting META-LEVEL .

sort InfoBar .

sort SubstTerm .
sort SubstTermList .
subsort SubstTerm < SubstTermList .


op {_|_} : Substitution Term -> SubstTerm [prec 40] . --- add precedence
op  nil  : -> SubstTermList .
op _::_  : SubstTermList SubstTermList -> SubstTermList 
[assoc id: nil] . --- add precedence


op geotheory       : -> Module .

op goalRules       : -> RuleSet .
op singleRules     : -> RuleSet .
op doubleRules     : -> RuleSet .
op splitRules      : -> RuleSet .
op existRules      : -> RuleSet .


op filterGoals     : RuleSet -> RuleSet .
op filterSingles   : RuleSet -> RuleSet .
op filterDoubles   : RuleSet -> RuleSet .
op filterSplitts   : RuleSet -> RuleSet .
op filterExists    : RuleSet -> RuleSet .


op generateSingles : RuleSet Term -> SubstTermList .
op gSingle         : Rule Term Nat -> SubstTermList .

op generateDoubles : RuleSet Term -> SubstTermList .
op gDouble         : Rule Term -> SubstTermList .

op generateGoals   : RuleSet Term -> SubstTermList .
op generateExists  : RuleSet Term -> SubstTermList .


op isDouble        : Rule -> Bool .
op isSingle        : Rule -> Bool .
op isSplit         : Rule -> Bool .
op isExist         : Rule -> Bool .
op isExistRS       : Term -> Bool . --- helper (RS = Right Hand)
op isGoal          : Rule -> Bool .

op exclusiveSingle : Rule -> Bool .
op exclusiveDouble : Rule -> Bool .
op exclusiveExist  : Rule -> Bool .


op goalMatch       : Term -> Bool .

op generateSplitts : RuleSet Term -> SubstTermList .

op crossProduct    : SubstTermList SubstTermList -> SubstTermList .
op crossSingle     : SubstTermList SubstTerm -> SubstTermList .


op applySubst      : SubstTermList -> Term .
op applySubst      : Substitution Term -> Term .
op applySubst      : Substitution TermList -> TermList .

op join            : Term Term -> Term .

op addDoublesMatch : Term Term -> Term .
op addSinglesMatch : Term Term -> Term .

op refreshSubst    : Term SubstTermList -> SubstTermList .

op updateFreshCnt  : Term -> Term .
op getLimit        : Int -> Nat .

op clash           : Substitution Substitution -> Bool .

--- simply reading with some headers
op [_]             : String -> InfoBar [format(nn y! o n)] .
op infobar         : String -> InfoBar .

op dt              : Term -> FactSet . 
op noResult        : -> [FactSet] .

op negative2fresh  : Term -> Term .
op negative2fresh  : TermList -> TermList .
op mnat2fresh      : Term -> Term .
op nq2s            : Qid -> String . --- 's_^X  -> 'NEWX

op existMatch      : Term SubstTerm -> Bool .
op splitMatch      : Term SubstTerm -> Bool .


var  M              : Module .
vars T1 T2 T3 T4    : Term .
vars Q1 Q2 Q3 Q4    : Qid .
vars RLS1 RLS2      : RuleSet .
vars RL1 RL2        : Rule .
vars N1 N2 N3 REST  : Nat .
vars SUB1 SUB2      : Substitution .
vars STL1 STL2      : SubstTermList .
vars ST1 ST2        : SubstTerm .
var  MRESULT        : [MatchPair?] .
var  FRESH          : Term .
var  METAFACTS      : Term .



eq geotheory = upModule('GeoTheory, false) .

eq goalRules    = filterGoals(   getRls( geotheory ) ) .
eq singleRules  = filterSingles( getRls( geotheory ) ) .
eq doubleRules  = filterDoubles( getRls( geotheory ) ) .
eq splitRules   = filterSplitts( getRls( geotheory ) ) .
eq existRules   = filterExists(  getRls( geotheory ) ) .

--- the clash function does not consider OPEN BINDINGS, i.e.,
---
--- clash( 'X:Int <- 'B:Int , 'X:Int <- 'A:Int ) == true
---
--- this should ideally lead to variable sharing, not a clash
--- but in this case it is ok, since we never match open terms, 
--- just so you know I know it's wrong :-)

ceq clash(V:Variable <- T1:Term ; S1:Substitution, 
          V:Variable <- T2:Term ; S2:Substitution) = true 
    if (T1:Term =/= T2:Term) .

eq clash(S1:Substitution, S2:Substitution) = false [owise] .


---  PRIORITY
---  
---  classify rules based on their apperance, what based on looks?
---  a rule can match several categories, and they will be ordered
---  as follows:
---
---   1. Splitters - the rules that has a right-hand disjunction
---   2. Exists    - the rules that introduce new constants
---   3. Others    - the rules that do not match 1. and 2. 
---                  will be given their actual status, in this
---                  category you will find: Single Double
---
---  what does this mean? well if you have a right hand side
---  disjunction, and you introduce new constants, and you
---  are a single rule, you will be placed in category 1.
---  since this has the highest priority. if you are a double
---  rule which introduces fresh constants, then you will be
---  placed in category 2. since this has higher priority then
---  being a double rule. so priority is based on classification
---  and the ordering given above.
---  
---  the reason for dividing this up into two sets of equations
---  is to avoid infinite recursion. the equations which start
---  off with a 'isSomething' will determine whether or not a
---  rule matches some criteria, but it might match more then
---  one set of criteria, so we have a set of 'exclusiveSomething'
---  which will make sure the priority ordering holds.


---  OPTIMIZE: filterAwaySomething(filterAwaySomethingElse(...RULES)
---  this will clearly be faster, but hopefully rewrites of
---  these terms are cached, so speed will be just as fast

eq  isDouble(rl '_`,_[NE:NeTermList] => T2 [label(Q1)] .) = true .
eq  isDouble(RL1) = false [owise] .

eq  isGoal(rl T1 => T2 [label(Q1)] .) = 
    if( T2 == 'Goal.Disjoint or T2 == 'False.Disjoint ) then
        true
    else
        false
    fi .

eq  isSingle(rl Q2[NE:NeTermList] => T2 [label(Q1)] .) =  
    if( Q2 =/= '_`,_ ) then
        true
    else
        false
    fi .

eq  isSplit(rl T1 => '_;_[NE:NeTermList]  [label(Q1)] .) = true .
eq  isSplit(RL1) = false [owise] .


eq  isExist( rl T1 => T2 [label(Q1)] . ) =
    if(isExistRS(T2)) then
        true
    else
        false
    fi .

eq  isExistRS(T1) =
    if(getTerm(metaReduce(geotheory, 'exrule[ T1 ])) == 'true.Bool) then
        true
    else
        false
    fi .

--- here we have the rules that ensures our priority ordering (@see PRIORITY)

eq  exclusiveSingle(RL1) =
    if( not (isGoal(RL1) or isExist(RL1) or isSplit(RL1)) and isSingle(RL1) ) then 
        true
    else 
        false
    fi .

eq  exclusiveDouble(RL1) =
    if( not (isGoal(RL1) or isExist(RL1) or isSplit(RL1)) and isDouble(RL1) ) then
        true
    else
        false
    fi .

eq  exclusiveExist(RL1) =
    if( not ( isSplit(RL1) ) and isExist(RL1) ) then
        true
    else
        false
    fi .



--- filterGoals(RuleSet) -> all goal-rules i.e. rules like this: rl Term => Goal .

eq  filterGoals(RL1 RLS1) =
    if( isGoal( RL1 ) ) then
        RL1 filterGoals( RLS1 )
    else
        filterGoals( RLS1 )
    fi .

eq  filterGoals(none) = none .

--- filterSingles(RuleSet) -> all rules which start with a single fact

eq  filterSingles(RL1 RLS1) =
    if( exclusiveSingle(RL1) ) then
        RL1 filterSingles( RLS1 )
    else
        filterSingles( RLS1 )
    fi .

eq  filterSingles(none) = none .


--- filterDoubles(RuleSet) -> all rules which start with more then one fact

eq  filterDoubles(RL1 RLS1) =
    if( exclusiveDouble(RL1) ) then
        RL1 filterDoubles( RLS1 )
    else
        filterDoubles( RLS1 )
    fi .

eq  filterDoubles(none) = none .

--- filterSplitts(RuleSet) -> all rules which have disjunctive conclusions

eq  filterSplitts(RL1 RLS1) =
    if( isSplit( RL1 ) ) then
        RL1 filterSplitts( RLS1 )
    else
        filterSplitts( RLS1 )
    fi .

eq  filterSplitts(none) = none .

--- filterExists(RuleSet) -> rules with fresh right-hand-side variables [not splitters]

eq  filterExists(RL1 RLS1) = 
    if( exclusiveExist(RL1) ) then
        RL1 filterExists(RLS1)
    else 
        filterExists(RLS1)
    fi .

eq  filterExists(none) = none .



eq  generateSingles(RL1 RLS1, T1) =
    gSingle(RL1, T1, 0) :: generateSingles(RLS1, T1) .
eq  generateSingles(none, T1) = nil .


ceq gSingle(rl T1 => T2 [label(Q1)] . RLS1, T3, N1) =
    
     if (MRESULT :: MatchPair) then
         { getSubstitution(MRESULT) | T2 } ::
         gSingle(rl T1 => T2 [label(Q1)] . RLS1, T3, N1 + 1)
     else 
         gSingle(RLS1, T3, 0) 
     fi
     
     if MRESULT := metaXmatch(geotheory, T1, T3, nil, 0, unbounded, N1) . 

eq  gSingle(none, T3, N1) = nil .
    

--- join matchings from single facts if no clash is present
--- rewrite rules can now match based on single instance
--- matching all elements of a right-side, like this:
---
---     facts: r(a,a),r(b,b)
---     rule : r(Y,Y),r(Z,X) = abc(Y,Z,X)
---
---  we see that our facts matches this rule in a number of ways
---  since r(a,a) alone matches the right-hand-side
---  and the fact r(b,b) matches the right-hand-side and also
---  combinations of these will match, so we create a cross-product
---  of all matchings which does not end up with conflicting matches.

eq  crossProduct(STL1, ST2 :: STL2) =
    crossSingle(STL1, ST2) ::
        crossProduct(STL1, STL2) .
eq  crossProduct(STL1, nil) = nil .
    
eq  crossSingle({ SUB1 | T1 } :: STL1, { SUB2 | T1 } ) =
     if(clash(SUB1, SUB2)) then
       crossSingle(STL1, { SUB2 | T1 } )
     else
       { SUB1 ; SUB2 | T1 } ::
       crossSingle(STL1, { SUB2 | T1 } )
     fi .
eq  crossSingle(nil, { SUB1 | T1 }) = nil .
    


eq  generateDoubles(RL1 RLS1, T1) = 
    gDouble(RL1, T1) :: generateDoubles(RLS1, T1) .

eq  generateDoubles(none, T1) = nil .

eq  gDouble(rl '_`,_[T1, NE:NeTermList] => T2 [label(Q1)] ., T3) =
    crossProduct(gSingle(rl T1 => T2 [label(Q1)] ., T3, 0),
                 gDouble(rl '_`,_[NE:NeTermList] => T2 [label(Q1)] ., T3)) .

ceq gDouble(rl '_`,_[T1] => T2 [label(Q1)] ., T3) =
    gSingle(rl T1 => T2 [label(Q1)] ., T3, 0) 
    if T1 =/= nil .

eq  gDouble(RL1, T3) = nil [owise] .
    


eq  generateGoals(RL1 RLS1, T1) =
    if(isDouble(RL1)) then
       generateDoubles(RL1, T1) :: generateGoals(RLS1, T1)
    else --- isSingle
       generateSingles(RL1, T1) :: generateGoals(RLS1, T1) 
    fi .

eq  generateGoals(none, T1) = nil . 


eq  goalMatch(T1) =
    if( generateGoals(goalRules, T1) == nil ) then
        false
    else
        true
    fi .


eq  generateSplitts(RL1 RLS1, T1) =
    if(isDouble(RL1)) then
        generateDoubles(RL1, T1) :: generateSplitts(RLS1, T1)
    else --- isSingle
        generateSingles(RL1, T1) :: generateSplitts(RLS1, T1)
    fi .

eq  generateSplitts(none, T1) = nil .


eq  generateExists(RL1 RLS1, T1) = 
    if(isDouble(RL1)) then
        generateDoubles(RL1, T1) :: generateExists(RLS1, T1)
    else ---isSingle
        generateSingles(RL1, T1) :: generateExists(RLS1, T1)
    fi .

eq  generateExists(none, T1) = nil .



eq  applySubst(ST1 :: ST2 :: STL2) = 
    join(applySubst(ST1) , applySubst(ST2 :: STL2)) .

eq  applySubst( nil ) = empty .

eq  applySubst({ SUB1 | Q1[ NE:NeTermList ]}) =
    Q1[ applySubst( SUB1, NE:NeTermList ) ] .

eq  applySubst( SUB1,  ( C1:Constant, TL:TermList )) = 
    C1:Constant, applySubst(SUB1, TL:TermList) .


eq  applySubst( V:Variable <- T1 ; SUB1, ( V:Variable, TL:TermList) ) =
    T1, applySubst( V:Variable <- T1 ; SUB1, (TL:TermList)) .

ceq applySubst( V1:Variable <- T1 ; SUB1, ( V2:Variable, TL:TermList) ) =
    V2:Variable, applySubst( V1:Variable <- T1 ; SUB1, (TL:TermList)) 
    if  V2:Variable =/= V1:Variable .

eq  applySubst( SUB1 , ( Q1[ TL:TermList ] , TL2:TermList ) ) =
    ( Q1[ applySubst(SUB1,  TL:TermList ) ] , applySubst(SUB1, TL2:TermList) ).

eq  applySubst( SUB1, ( empty ) ) = empty .


eq  join('_`,_[NE:NeTermList], '_`,_[NE2:NeTermList]) =
    '_`,_[NE:NeTermList, NE2:NeTermList] .

ceq join('_`,_[NE:NeTermList], Q1[NE2:NeTermList]) =
    '_`,_[NE:NeTermList, Q1[NE2:NeTermList]] if (Q1 =/= '_`,_) .

ceq join(Q1[NE:NeTermList], '_`,_[NE2:NeTermList]) =
    '_`,_[Q1[NE:NeTermList], NE2:NeTermList] if (Q1 =/= '_`,_) .

ceq join(Q1[NE:NeTermList], Q2[NE2:NeTermList]) =
    '_`,_[Q1[NE:NeTermList], Q2[NE2:NeTermList]] 
    if (Q1 =/= '_`,_) and (Q2 =/= '_`,_) .

eq  join(empty, T1) = T1 .
eq  join(T1, empty) = T1 .



ceq refreshSubst( T1, { SUB1 | T2 } :: STL1 ) = 
    { SUB1 | FRESH } :: refreshSubst( 
                        getTerm( metaReduce( geotheory, 'max[ 'remax[ FRESH ], T1 ] )),
                        STL1 )
    if FRESH := getTerm( metaReduce(geotheory, 'refresh[ T1, T2 ]) ) .


eq  refreshSubst( T1 , nil ) = nil .

eq  updateFreshCnt(T1) = getTerm(metaReduce(geotheory, 'maximum[ T1 ]) ) .

eq  infobar(S:String) = [S:String] .
eq  dt(T1) = downTerm(T1, noResult) .



--- these equations will converte negative terms to fresh variables
--- which makes it possible to match a right hand side of an equation
--- to see if we can avoid adding further elements to our domain:

--- typical right hand side of a rule:    dom(-1),r(-1,X)
--- will be turned into              :    dom(NEW1:Int),r(NEW1:Int,X)

--- which we then can match with our factset to see if we need to 
--- apply the substitution (and generate the new constants)

--- this is the scenario; do we need to apply this substitution
--- 
---     X <- 1 ; Y <- 2            
---
--- on this rule
---
---  s(X,Y) => dom(-1),r(-1,X),r(-1,Y)
---
--- when we have these facts inside our factset:
---
---  dom(1),dom(2),dom(3),s(1,2),r(2,1),r(2,2)
---
--- first apply the substitution got from matching
---
---     s(1,2) with the right hand side of the rule
---
---     X <- 1 ; Y <- 2            
---     
--- then we end up with
---
--- dom(-1), r(-1,1),r(-1,2)
---
--- this will then be fresh'ed up by these equations like this
---
--- dom(NEW1:Int),r(NEW1:Int,1),r(NEW1:Int,2)
---
--- does it match something we have inside our factset?
---
--- yes it does : dom(2), r(2,1), r(2,2)
---
--- so there is no need to apply this rule again with
--- this substitution


--- TermList

eq  negative2fresh( ( T1 , NE:NeTermList ) ) =
    negative2fresh( T1 ), negative2fresh( NE:NeTermList ) .

eq  negative2fresh( nil ) = nil .

--- Term

ceq negative2fresh(Q1[TL:TermList]) =
    Q1[negative2fresh(TL:TermList)] 
    if Q1 =/= '-_ .

eq  negative2fresh(C:Constant) = C:Constant .

eq  negative2fresh('-_[ T1 ] ) = --- T1 => 's_[.. '0.Zero ..]
    mnat2fresh( '-_[ T1 ] ) .

eq  mnat2fresh( '-_[ 's_[ T1 ] ] ) = 'NEW1:Int .

eq  mnat2fresh( '-_[ Q1[ T1 ] ] ) = qid( nq2s(Q1) + ":Int") .


eq  nq2s( Q1 ) =
    "NEW" + substr(string(Q1), 3, length(string(Q1))) .


ceq existMatch(METAFACTS, { SUB1 | T1 }) =
    
    if( metaXmatch(geotheory, 
                   negative2fresh( applySubst( { SUB1 | T1 } ) ),
                   METAFACTS, nil, 0, unbounded, 0) :: MatchPair ) then
        true
    else
        false
    fi
    if T2 := negative2fresh( applySubst( { SUB1 | T1 } ) )
-----    [ print "[ existMatch ]  T2 " T2 ] 
.



endm


mod ObjectLevelRules is

pr SetRewrite .

sort Search .
sort SearchStack .
sort Branch .
sort Branches .
subsort Branch < Branches .


op <_|_|_|_|_|_> : 
Term Term SubstTermList SubstTermList SubstTermList SubstTermList -> Branch 
[ format(nm! o d d d d d d d d d d m! o) ] .

op void     : -> Branches .
op __       :  Branches Branches -> Branches [ assoc id: void prec 70 ] .
op stack_   :  Branches -> SearchStack  [ prec 77 ] .
op __       :  Branch SearchStack -> Search [ format(d g! o) prec 80 ] .
op valid    : -> Search .


op initSearch : FactSet -> Search .
op initSearch : FactSet Nat -> Search .

op applyOneRule : SubstTerm Term -> Term .
op applyOneRule : Term Term SubstTerm -> Term .


vars AlreadyPresent                   : Bool .
vars Assignments                      : Substitution .
vars Path                             : Branch .
vars Paths                            : Branches .
vars Facts  Max  RightSide  MoreFacts : Term .
vars ExistSub ForkSub RegSub1 RegSub2 : SubstTermList .


eq initSearch(FS:FactSet) = initSearch(FS:FactSet, 100) .
eq initSearch(FS:FactSet, N:Nat) =
 < upTerm(FS:FactSet) | upTerm(N:Nat) | nil | nil | nil | nil >  stack  void  . 

eq applyOneRule( { Assignments  | RightSide } , Facts ) =
getTerm( metaReduce(
          geotheory,
            join( 
applySubst( { Assignments | RightSide } ), Facts ) ) ) .


ceq applyOneRule(Facts, Max, { Assignments | RightSide } ) =
    if( AlreadyPresent ) then
        Facts 
    else
        getTerm( metaReduce(geotheory, MoreFacts) )
    fi
if AlreadyPresent := existMatch( Facts, { Assignments | RightSide } ) 
/\ MoreFacts :=  join( Facts , applySubst ( refreshSubst( Max, { Assignments | RightSide } )))
----- [ print " AlreadyPresent " AlreadyPresent ]
.


crl[gen-regular-one]:
   < Facts | Max |   nil   | RegSub2 | ExistSub | ForkSub > stack  Paths 
=> 
   < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub > stack  Paths
if RegSub1 := generateSingles( singleRules, Facts ) 
----- [ print "gen-regular-one" ]
.
 
crl[gen-regular-two]:
    < Facts | Max | RegSub1 |   nil   | ExistSub | ForkSub > stack Paths 
=> 
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub > stack Paths 
if RegSub2 := generateDoubles( doubleRules, Facts ) 
----- [ print "gen-regular-two" ]
.

crl[gen-exists]:
    < Facts | Max | RegSub1 | RegSub2 |    nil   | ForkSub > stack Paths 
=> 
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub > stack Paths 
if ExistSub := generateExists( existRules, Facts ) 
----- [ print "gen-exists" ]
.

crl[gen-fork]:
    < Facts | Max | RegSub1 | RegSub2 | ExistSub |  nil    > stack Paths 
=> 
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub > stack Paths 
if ForkSub := generateSplitts( splitRules, Facts ) 
----- [ print "gen-exists" ]
.

crl[add-ones]:
    < Facts | Max | { Assignments | RightSide } :: RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Paths 
=> 
    < MoreFacts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Paths 
if MoreFacts := applyOneRule({ Assignments | RightSide } ,  Facts ) 
----- [ print "add-ones" ]
.

crl[add-twos]:
    < Facts | Max | RegSub1 | { Assignments | RightSide } :: RegSub2 | ExistSub | ForkSub  > stack Paths 
=> 
    < MoreFacts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Paths 
if MoreFacts := applyOneRule({ Assignments | RightSide } ,  Facts ) 
----- [ print "add-twos"  ]
.

crl[add-exists]:
    < Facts | Max | RegSub1 | RegSub2 | { Assignments | RightSide } :: ExistSub | ForkSub  > stack Paths 
=> 
    < MoreFacts | updateFreshCnt( MoreFacts ) | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Paths 
if MoreFacts := applyOneRule(Facts, Max , { Assignments | RightSide }) 
----- [ print "add-exists" ]
.

crl[closed-path]:
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack void
=> 
    valid
if goalMatch( Facts )
----- [ print " >>>> closed a path " ]
.

crl[closed-path]:
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Path Paths
=> 
    Path stack Paths 
if goalMatch( Facts ) 
----- [ print " >>>> closed a path <<<<" ]
.

crl[add-fork]:
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | { Assignments | '_;_[ T:Term ] } :: ForkSub  > stack Paths 
=> 
    < MoreFacts | Max | RegSub1 | RegSub2 | ExistSub | ForkSub  > stack Paths 
if MoreFacts := applyOneRule(Facts, Max , { Assignments | T:Term }) 
----- [ print "add-fork-single "  ]
.

crl[add-fork]:
    < Facts | Max | RegSub1 | RegSub2 | ExistSub | { Assignments | '_;_[T:Term, TL:NeTermList ] } :: ForkSub  > stack Paths 
=> 
    < MoreFacts | updateFreshCnt( MoreFacts ) | RegSub1 | RegSub2 | 
      ExistSub | { Assignments | '_;_[ TL:NeTermList ] } :: ForkSub  > 
stack 
< Facts | Max | RegSub1 | RegSub2 | ExistSub | { Assignments | '_;_[ TL:NeTermList ] } :: ForkSub  > Paths 
if MoreFacts := applyOneRule(Facts, Max , { Assignments | T:Term }) 
----- [ print "add-fork-double" ]
.

endm


--- set print attribute on or not
%s

rewrite in ObjectLevelRules :
  < upTerm( %s ) | upTerm( %d ) | nil | nil | nil | nil >
  stack void 
  .


q
"""


