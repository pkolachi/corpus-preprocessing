
from globalimports import *;
import random_utils;
import conll_utils;
import os.path;

with random_utils.smart_open(sysargv[1], 'wb') as idsfile:
  for origfilename in sysargv[2:]:
    with random_utils.smart_open(origfilename) as infile:
      prefix             = os.path.split(origfilename)[1].replace('.conll.bz2', '');
      conll_sentences    = conll_utils.sentences_from_conll(infile);
      sent_ids           = ('%s-%s' %(prefix, str(idx).zfill(9)) for idx, sent in enumerate(conll_sentences, start=1) if len(sent) <= 80); 
      random_utils.lines_to_filehandle(idsfile, sent_ids);


