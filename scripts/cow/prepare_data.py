#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 

import os ; 
import sys ; 

def unxmlize(string) :
  string = string.replace('&quot;', '"') ;
  string = string.replace('&apos;', "'") ;
  string = string.replace('&lt;'  , '<') ;  
  string = string.replace('&gt;'  , '>') ;  
  string = string.replace('&amp;' , '&') ;
  return string ; 

def main_loop() :
  # DEFINE THESE FOR EACH CORPUS BEFORE RUNNING IT
  FORM = 0 ; LEMMA = 2 ; POSTAG = 1 ; 
  # For French corpus, since it is fully parsed 
  FORM = 0 ; LEMMA = 2 ; POSTAG = 1 ; CPOSTAG = 3 ; MTAG = 4 ; ID = 5 ; HEAD = 7 ; DEP = 6 ; 
  FILTER  = 0 ;
  MAX_LEN = 100 ; 
  for fpth in sys.argv[1:-1] :
    fpref = os.path.splitext(os.path.split(fpth)[1])[0] ;  # prefix
    sentc = 0 ; 
    lines = [] ;
    for l in ru.lines_from_file(fpth) :
      if l.startswith('<s') :
        sentc += 1 ; 
      elif l.strip() == '</s>' :
        if FILTER and len(lines) >= MAX_LEN : 
          lines = [] ; 
        else : 
          # convert sentence to CoNLLU representation
          # yield meta-information
          yield "# sent_id = {0}-{1}".format(fpref, str(sentc).zfill(9)) ;
          for i,e in enumerate(lines, start=1) :
            #cols = [str(i), e[FORM], e[LEMMA], '_', e[POSTAG], '_', '_', '_', '_', '_'] ;
            cols  = [e[ID], e[FORM], e[LEMMA], e[CPOSTAG], e[POSTAG], e[MTAG], e[HEAD], e[DEP], '_', '_'] ;  # for French only
            yield '\t'.join(cols) ; 
          yield '' ;
          lines = [] ;
      else :
        l = unxmlize(l) ;
        lines.append(l.strip().split('\t')) ; 

ru.lines_to_file(sys.argv[-1], main_loop()) ; 
