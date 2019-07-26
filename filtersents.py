#!/usr/bin/env python3

from globalimports import *;
import random_utils, conll_utils;

def work():
  sel_ids = dict((int(idx), True) \
      for idx in random_utils.lines_from_file(sysargv[1]));
  buf, offset = [], 0;
  conll_utils.FIELDS = conll_utils.CONLL07_COLUMNS;
  for conllfile in sysargv[2:]:
    #reader  = random_utils.lines_from_file(sys.argv[2]);
    with random_utils.smart_open(conllfile) as infile:
      for conll_sent in conll_utils.sentences_from_conll(infile):
        offset += 1;
        if offset in sel_ids:
          yield conll_sent;

def work2():
  sel_ids = dict((int(idx), True) \
      for idx in random_utils.lines_from_file(sysargv[1]));
  random_utils.lines_to_filehandle(stdout, (line for idx, line in enumerate(random_utils.lines_from_file(sysargv[2]), start=1) if idx in sel_ids));
  return;


#conll_utils.sentences_to_conll(stdout, work());
work2();
