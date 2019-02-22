#!/usr/bin/env python3

import sys;
import conll_utils as cu;
import random_utils as ru;
import os, os.path;

cu.FIELDS = cu.CONLLU_COLUMNS;

def merged_output(idsList, filesList):
  for filepath in filesList:
    conll_sents = cu.sentences_from_conll(ru.lines_from_file(filepath));
    for meta, sent in conll_sents:
      metal = meta.split('\n');
      newmetal = []
      for m in metal:
        if m.startswith('# sent'):
          newmetal.append(u'# sent_id = %s' %(next(idsList)));
        else:
          newmetal.append(m);
      yield (u'\n'.join(newmetal), sent);


cleanids = list(ru.lines_from_file(sys.argv[1]));
cleanids = iter(cleanids);

ru.lines_to_file(sys.argv[-1], \
    cu.sentences_to_conll(merged_output(cleanids, sys.argv[2:-1])));

#filesList = os.listdir(sys.argv[2]);
#filesList = [os.path.join(sys.argv[2], filename) for filename in filesList];
#ru.lines_to_file(sys.argv[3], \
#    cu.sentences_to_conll(merged_output(cleanids, filesList)));

