# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="ageorges"
__date__ ="$Feb 8, 2012 4:02:38 PM$"

def catMaybeValues(d):
    d_ = dict()
    for k,v in d.iteritems():
       if v != None: 
           d_[k] = v
    return d_
