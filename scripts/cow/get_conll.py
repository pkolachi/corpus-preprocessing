#!/usr/bin/env python3

from collections import defaultdict ; 
import itertools as it ; 
import re;

from globalimports import *;
import random_utils as ru ;
import conll_utils  as cu ;

def parse_attributes(attr_str):
  attr_str = attr_str.strip().split();
  docid, bdc, bpc = '-NONE-', '-NONE-', '-NONE-' ;
  for attr in attr_str:
    if attr.startswith('id'):
      docid = attr;
    elif attr.startswith('bdc'):
      bdc = attr;
    elif attr.startswith('bpc'):
      bpc = attr;
  return "{0},{1},{2}".format(docid, bdc, bpc);

def sentences_from_xmlfile(filename):
  sent = [];
  for line in ru.lines_from_file(filename):
    if line.startswith('<s '):
      # find the comment; but initialize sent first;
      sent = [];
      comment = parse_attributes(line[2:-1]);
    elif line == '</s>':
      yield (comment, sent);
    else:
      fields = re.split('\s+', line.strip());
      sent.append(fields);

def replace_html(word) :
  word = word.replace('&amp;' , '&') ;
  word = word.replace('&lt;'  , '<') ; 
  word = word.replace('&gt;'  , '>') ;
  word = word.replace('&quot;', '"') ; 
  word = word.replace('&apos;', "'") ;
  return word ; 

def fields2conll(sent, xmlfields=None):
  # Modified on 15th July 2018 to make parsing xml sentence flexible
  global FIELDS ; 
  xmlfields = xmlfields if xmlfields else FIELDS ;
  csent = [defaultdict(lambda: '_') for _ in sent[1]] ; 
  for idx, wordentry in enumerate(sent[1], start=1) : 
    for field in cu.CONLL07_COLUMNS :
      if field in xmlfields :
        if field in ['form', 'lemma'] :
          wordentry[xmlfields.index(field)] = replace_html(wordentry[xmlfields.index(field)]) ; 
        csent[idx-1][field] = wordentry[xmlfields.index(field)] ; 
    if 'id' not in xmlfields :
      csent[idx-1]['id'] = str(idx) ; 
  return ("# sent {0}".format(sent[0]), csent) ; 

def prepare_mate(sent, xmlfields=None):
  global FIELDS09 ; 
  xmlfields  = xmlfields if xmlfields else FIELDS09 ; 
  csent = [defaultdict(lambda: '_') for _ in sent[1]] ; 
  for idx, wordentry in enumerate(sent[1], start=1) :
    for field in cu.CONLL09_COLUMNS : 
      if field in xmlfields : 
        if field in ['form', 'lemma', 'plemma'] :
          wordentry[xmlfields.index(field)] = replace_html(wordentry[xmlfields.index(field)]) ; 
        csent[idx-1][field] = wordentry[xmlfields.index(field)] ; 
    if 'id' not in xmlfields :
      csent[idx-1]['id'] = str(idx) ; 
  return (sent[0], csent) ;

MAX_PART_SIZE  = 100000;
SMALL_BUF_SIZE = int(MAX_PART_SIZE/4);

mate_outconllprefix = sysargv[1].replace('.xml.gz', '');
mate_outconllprefix = mate_outconllprefix.replace('01', '');
partids = 1;
mate_outconllfilename = '%s_part%s.mateinput.conll09.xz' %(mate_outconllprefix, str(partids).zfill(4));
mate_outconll = ru.smart_open(mate_outconllfilename, 'wb');
PART_BUF = [];
cur_sentences_count = 0;

#FIELDS  = ['word', 'lemma', 'postag'] ; 
#_FIELDS = ['word', 'postag', 'lemma'] ; 
FIELDS   = ['form', 'postag', 'lemma', 'cpostag', 'feats', 'id', 'deprel', 'head'] ;     # for French
with ru.smart_open('%s.clean.lines-retained.xz' %(mate_outconllprefix), 'wb') as idsfile:
  for origfilename in sysargv[1:]:
    conlloutfilename = origfilename.replace('.xml', '.conll');
    if conlloutfilename.endswith('.gz'):
      conlloutfilename = conlloutfilename.replace('.gz', '.xz') ;
    with ru.smart_open(conlloutfilename, 'wb') as localoutfile:
      original_sentences  = sentences_from_xmlfile(origfilename);
      conll_sentences     = map(fields2conll, original_sentences);
      buf_conll_sentences = conll_sentences ; 
      #buf_conll_sentences = it.islice(conll_sentences, SMALL_BUF_SIZE);
      #buf_conll_sentences = list(buf_conll_sentences);
      # first write out this buf to local output file;
      ru.lines_to_filehandle(localoutfile, cu.sentences_to_conll07(buf_conll_sentences)) ;
      
      '''
        mate_sentences = map(prepare_mate, buf_conll_sentences); 
        sent_ids       = [X[0] for X in buf_conll_sentences if len(X[1]) <= 200];
        mate_sentences = [X    for X in mate_sentences if len(X) <= 200];

        if cur_sentences_count + len(PART_BUF) + len(mate_sentences) <= MAX_PART_SIZE:
          if PART_BUF:
            cu.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = [];
            cur_sentences_count += len(PART_BUF);
          ru.lines_to_filehandle(idsfile, sent_ids);
          cu.sentences_to_conll09(mate_outconll, mate_sentences);
          cur_sentences_count += len(mate_sentences);
          continue;

        if cur_sentences_count + len(PART_BUF) <= MAX_PART_SIZE:
          if PART_BUF:
            cu.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = [];
            cur_sentences_count += len(PART_BUF);
          continue;


        else:
          if cur_sentences_count + len(PART_BUF) <= MAX_PART_SIZE:
            cu.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = ;
            cur_sentences_count += len(PART_BUF);
        '''

        #ru.lines_to_filehandle(idsfile, (X[0] for X in buf_conll_sentences if len(X[1]) < 100));
      '''
        PART_BUF.extend(map(prepare_mate, filter(lambda X: len(X[1]) < 100, buf_conll_sentences)));
        if len(PART_BUF) > MAX_PART_SIZE:
          ru.lines_to_filehandle(mate_outconll, cu.sentences_to_conll09(PART_BUF[:MAX_PART_SIZE]));
          mate_outconll.close();
          PART_BUF = PART_BUF[MAX_PART_SIZE:];
          partids += 1;
          mate_outconllfilename = '%s_part%s.mateinput.conll09.bz2' %(mate_outconllprefix, str(partids).zfill(4));
          mate_outconll = ru.smart_open(mate_outconllfilename, 'wb');
        '''
        #if len(buf_conll_sentences) < SMALL_BUF_SIZE:        break;
#if len(PART_BUF):
#  ru.lines_to_filehandle(mate_outconll, cu.sentences_to_conll09(PART_BUF));
