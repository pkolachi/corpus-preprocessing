#!/usr/bin/env python

import itertools, re;
import random_utils;

PARA_CORP = {
    'sv-en':('/Users/prakol/Documents/chalmers-work/corpus-preprocessing/corpora-resources/wmt-europarl/parallel/europarl-v7.sv-en.raw', 'sv', 'en'), \
    'fi-en':('/Users/prakol/Documents/chalmers-work/corpus-preprocessing/corpora-resources/wmt-europarl/parallel/europarl-v7.fi-en.raw', 'fi', 'en') \
    };
PARA_DB = dict();

for langpair, corpdets in PARA_CORP.iteritems():
    srcfile = random_utils.lines_from_file('%s.%s' %(corpdets[0],corpdets[1]));
    tgtfile = random_utils.lines_from_file('%s.%s' %(corpdets[0],corpdets[2]));

    for srcsent, tgtsent in itertools.izip(srcfile, tgtfile):
        PARA_DB.setdefault(corpdets[1], {}).setdefault(corpdets[2], {})[srcsent.strip()] = tgtsent.strip();
        PARA_DB.setdefault(corpdets[2], {}).setdefault(corpdets[1], {})[tgtsent.strip()] = srcsent.strip();

langList = PARA_DB.keys();
for lang in PARA_DB.keys():
    if len(PARA_DB[lang]) == len(PARA_DB.keys())-1:
        pivotLang = lang;
for langpair in itertools.combinations(langList, 2):
    if PARA_DB.get(langpair[0], {}).get(langpair[1], None):
        continue;
    else:
        commSentences = set(PARA_DB[pivotLang][langpair[0]].keys()) & set(PARA_DB[pivotLang][langpair[1]].keys());
        srclang, tgtlang = sorted(langpair);
        #print srclang, tgtlang, len(commSentences);
        new_src_file = 'newscommentary-v6.%s-%s.raw.%s' %(srclang,tgtlang,srclang);
        new_tgt_file = 'newscommentary-v6.%s-%s.raw.%s' %(srclang,tgtlang,tgtlang);
        random_utils.lines_to_file(new_src_file, PARA_DB[pivotLang][langpair[0]][pivotSentence] for pivotSentence in commSentences);
        random_utils.lines_to_file(new_tgt_file, PARA_DB[pivotLang][langpair[1]][pivotSentence] for pivotSentence in commSentences);
