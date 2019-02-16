#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 
from itertools import chain ; 
import sys ; 
import os.path ; 

DEF = 2 ;
INFILES = '' if len(sys.argv) < DEF    else sys.argv[:-1] ; 
OUTFILE = '' if len(sys.argv) < DEF+1  else sys.argv[-1]  ; 

def main_loop() :
  global INFILES ;
  INFILES = sorted(INFILES) ; 
  clns    = (ln for inf in INFILES for ln in ru.lines_from_file(inf)) ; 
  docpath = '/corpora/corpora-resources/wac/ukWac/split/' ; 
  output_tok_text = True ; 

  # newdoc  id information is spread everywhere
  # do not replace it with one path information
  # extract directory and filename from the newdoc id information
  # newpar: skip this line. pretty useless
  # replace sent_id information with new sentid
  # output text metainfo as usual 
  # if tok_text option is provided, add new metainfo line called tok_text
  # output CoNLLu lines for the sentence as usual
  cbuf   = [] ; 
  tokens = [] ; 
  pcount = 0  ; 
  scount = 0  ;
  decerr = 0 ; 

  for inf in INFILES : 
    with ru.smart_open(inf) as infile : 
      for ln in infile : 
        ln = ln.strip() ;
        try : 
          ln = ln.decode('utf-8') ;  
        except UnicodeDecodeError : 
          decerr += 1 ; 
          ln = ln.decode('utf-8', errors='replace') ; 

        if ln == '# newpar' : 
          # skip this line 
          pcount += 1 ; 
          pass ; 
        elif ln.startswith('# newdoc id') : 
          docid = ln.split('=', 1)[1].strip() ;
          fname = '/'.join(docid.rsplit('/',2)[1:]) ;
          fpref = fname.rsplit('.',1)[0] ; 
          docm  = '# new_doc  = {0}'.format(docpath+fname) ; 
          yield docm ; 
          pcount = 0 ; 
          scount = 0 ; 
        elif ln.startswith('# text') :
          _, sid = ln.split('=', 1) ;
          newln = '# raw_text = {0}'.format(sid.strip()) ; 
          yield newln ; 
        elif ln.startswith('# sent_id') : 
          scount += 1 ; 
          fnid  = '{0}:{1}:{2}'.format(fpref, pcount, scount) ; 
          yield '# sent_id  = {0}'.format(fnid) ; 
        elif not ln : 
          # empty line
          # dumpy as-is unless output_tok_text option is true 
          if output_tok_text : 
            tok_text = ' '.join(tokens) ; 
            yield '# tok_text = {0}'.format(tok_text) ; 
            for cn in cbuf :
              yield cn ; 
            tokens = [] ; 
            cbuf   = [] ;
          yield ln ; 
        else : 
          # this is node in CoNLLu format
          if output_tok_text : 
            cbuf.append(ln) ; 
            fs = ln.split('\t') ; 
            try : 
              _ = int(fs[0]) ; 
              tokens.append(fs[1]) ;
            except ValueError : 
              # this is not a regular node; do not add it to tokens 
              pass ;
          else :
            yield ln ;
  print("Total number of decoding errors: {0}".format(decerr), file=sys.stderr) ; 


ru.lines_to_file(OUTFILE, main_loop()) ;
