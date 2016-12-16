#!/usr/bin/env python3

from globalimports import *;
import random_utils;
import conll_utils;
import sys;


def get_lingdata_UD():
  ling_info = {}; 
  # keys can be 'ARGTYPES'; 'SPECIALDEPRELTYPES'; 'SPECIALDEPRELTYPESDETAIL';  
  return ling_info;

def get_extraction_variables():
  extract_metaInfo = {};
  # keys can be 'INCLUDEGOVCAT'; 'INCLUDEDIR'
  extract_metaInfo['INCLUDEGOVCAT'] = True; # should include cat of governor
  extract_metaInfo['INCLUDEDIR'] = True;    # should include direction of attachment to governor
  return extract_metaInfo; 

def stag_extraction(*args):
  sigTable, adjTable, bigramTable, lhsTable, rhsTable, rootTable = args;
  def extract4sent(conll_sent):
    word_table = dict((int(edge['id']), edge['form'])   for edge in conll_sent);
    cat_table  = dict((int(edge['id']), edge['postag']) for edge in conll_sent);
    governor_table = defaultdict(list);
    for edge in conll_sent:
      governor_table[int(edge['head'])].append(int(edge['id']));
    for edge in conll_sent:
      if edge['argstatus'] == ARGUMENT:
        pass;

  return extract4sent;

def main():
  if len(sysargv) < 2:
    print("Usage: {0} conll-file [lexspec] [maxLexSpec]".format(sysargv[0]), file=sys.stderr);
    sysexit(1);

  if len(sysargv) > 2:
    lexical_items = random_utils.lines_from_file(sysargv[2]);
    lexical_table = dict((word, True) for word in lexical_items);

  LING_MODEL = get_lingdata_UD();
  EXTRACT_ENVIRON = get_extraction_variables();
  sigTable, adjTable, bigramTable, lhsTable, rhsTable, rootTable = \
      tuple([{} for _ in range(6)]);
  with random_utils.smart_open(sysargv[1]) as infile:
    encinstream = random_utils.lines_from_filehandle(infile);
    conll_sents = conll_utils.sentences_from_conll(encinstream);
    aug_conll_sents = map(mark_argadjuncts, conll_sents);
    extractor = stag_extraction(sigTable, adjTable, bigramTable, lhsTable, \
        rhsTable, rootTable);
    stag_conll_sents = map(extractor, aug_conll_sents);

  return;

if __name__ == '__main__':
  main();
  sysexit(0);

