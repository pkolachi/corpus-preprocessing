#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 
import sys ; 
import os.path ; 

if len(sys.argv) < 2:
  print("./{0} <cleanids-file> <prefix> <docid> <conllu-in> <conllu-out>".format(sys.argv[0])) ;
  sys.exit(1) ; 

DEF = 5 ; 
INFILE  = '' if len(sys.argv) < DEF    else sys.argv[DEF-1] ; 
OUTFILE = '' if len(sys.argv) < DEF+1  else sys.argv[DEF]   ; 

def main_loop() : 
  clns = ru.lines_from_file(INFILE) ; 
  sids = ru.lines_from_file(sys.argv[1]) ; 
  pref = sys.argv[2] ;
  dcid = sys.argv[3] ; 
  output_tok_text = True ; 

  # newdoc  id information is spread everywhere
  # replace it with one path information
  # extract splitid from the newdoc id information
  # newpar: skip this line. pretty useless
  # replace sent_id information with new sentid
  # output text metainfo as usual 
  # if tok_text option is provided, add new metainfo line called tok_text
  # output CoNLLu lines for the sentence as usual
  cbuf = [] ; 
  tokens = [] ; 
  yield '# newdoc id = {0}'.format(dcid) ; 
  for ln in clns : 
    ln = ln.strip() ; 
    if ln == '# newpar' : 
      # skip this line 
      pass ; 
    elif ln.startswith('# newdoc id') : 
      docid = ln.split('=', 1)[1].strip() ; 
      splitid = os.path.splitext(os.path.split(docid)[1])[0][-3:] ; 
    elif ln.startswith('# text') :
      _, sid = ln.split('=', 1) ;
      newln = '# raw_text = {0}'.format(sid.strip()) ; 
      yield newln ; 
    elif ln.startswith('# sent_id') : 
      newid = next(sids) ; 
      newid = newid.strip() ; 
      #fnid  = '{0}:{1}:split.{2}'.format(pref, newid, splitid) ; 
      fnid  = '{0}:split.{1}:{2}'.format(pref, splitid, newid) ; 
      yield '# sent_id  = {0}'.format(fnid) ; 
    elif not ln.strip() : 
      # empty line
      # dumpy as-is unless output_tok_text option is true 
      if output_tok_text : 
        tok_text = ' '.join(tokens) ; 
        yield '# tok_text = {0}'.format(tok_text) ; 
        for cn in cbuf :
          yield cn ; 
        tokens = [] ; 
        cbuf   = [] ;
      yield ln.strip() ; 
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


  #make sure that at the end of processing, sids is empty
  sids = list(sids) ; 
  if len(sids) :
    print("Sentence IDs list not empty towards the end. Misaligned IDs and CoNLLu sentences", file=sys.stderr) ; 
    print("Misaligned ID ptr:\t{0}".format(sids[0]), file=sys.stderr) ; 

ru.lines_to_file(OUTFILE, main_loop()) ; 
