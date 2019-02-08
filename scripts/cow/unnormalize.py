#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 
import sys ; 

def unxmlize(string) :
  string = string.replace('&quot;', '"') ;
  string = string.replace('&apos;', "'") ;
  string = string.replace('&lt;'  , '<') ;  
  string = string.replace('&gt;'  , '>') ;  
  string = string.replace('&amp;' , '&') ;
  return string ; 

def main_loop2() :
  for li in ru.lines_from_file(sys.argv[1], large=True) :
    if not li.strip() :
      # empty line
      yield li.strip() ;
    elif li.startswith('#') :
      # meta-comments
      li = unxmlize(li) ;
      yield li.strip() ;
    else:
      # actual nodes in the parsed corpus
      ts = li.split('\t') ;
      ts[1] = unxmlize(ts[1]) ;
      ts[2] = unxmlize(ts[2]) ;
      yield '\t'.join(ts) ;

def main_loop() :
  lines = ru.lines_from_file(sys.argv[1]) ; 
  nls = map(unxmlize, lines) ; 
  return nls ; 

ru.lines_to_file('', main_loop()) ; 

