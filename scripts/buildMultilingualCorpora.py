#!/usr/bin/env python

import os;
from itertools import imap, izip, izip_longest;
from collections import defaultdict;
import random_utils;

PARA_CORP = {\
	'sv-en':('/Users/prakol/Documents/chalmers-work/gf-translation/stat-mt/moses-models/baselines/europarl.en-sv/data-partitions/europarl-v7.sv-en.uniq.raw', 'sv', 'en'), \
	'bg-en':('/Users/prakol/Documents/chalmers-work/gf-translation/stat-mt/moses-models/baselines/europarl.en-bg/data-partitions/europarl-v7.bg-en.uniq.raw', 'bg', 'en')};
#PARA_CORP = {\
#	'sv-en':('/Users/prakol/Documents/chalmers-work/gf-translation/stat-mt/moses-models/baselines/europarl.en-sv/phrase-based/corpus/europarl.tok.1', 'sv', 'en'), \
#	'bg-en':('/Users/prakol/Documents/chalmers-work/gf-translation/stat-mt/moses-models/baselines/europarl.en-bg/phrase-based/corpus/europarl.tok.1', 'bg', 'en')};
outputPrefix = 'europarl-v7.sv-bg-en.raw';

PARA_DB = defaultdict(lambda: defaultdict(lambda: defaultdict()));

for langpair, corpdets in PARA_CORP.iteritems():
    srcfilename = '%s.%s' %(corpdets[0], corpdets[1]); 
    tgtfilename = '%s.%s' %(corpdets[0], corpdets[2]);
    if not (os.path.isfile(srcfilename) or os.path.isfile(tgtfilename)):
	srcfilename, tgtfilename = '%s.bz2' %(srcfilename), '%s.bz2' %(tgtfilename);

    srcfile = random_utils.lines_from_file(srcfilename);
    tgtfile = random_utils.lines_from_file(tgtfilename);

    for srcsent, tgtsent in izip_longest(srcfile, tgtfile):
	PARA_DB[corpdets[2]][corpdets[1]][tgtsent.strip()] = srcsent.strip();
	PARA_DB[corpdets[1]][corpdets[2]][srcsent.strip()] = tgtsent.strip();

langList = PARA_DB.keys();
for lang in PARA_DB.keys():
    if len(PARA_DB[lang]) == len(PARA_DB.keys())-1:
	pivotLang = lang;
possibleLanguages = PARA_DB[pivotLang].keys();

unionSentences = set();
for lang in possibleLanguages:
    unionSentences = unionSentences | set(PARA_DB[pivotLang][lang].iterkeys());
unionSentences = sorted( unionSentences );

MULTI_DB = dict();

for sentence in unionSentences:
    allPresent = True;
    for lang in possibleLanguages:
	if not PARA_DB[pivotLang][lang].has_key(sentence):
	    allPresent = False;
	    break;
    if allPresent:
	for lang in possibleLanguages:
	    MULTI_DB.setdefault(lang, []).append(PARA_DB[pivotLang][lang][sentence]);
	MULTI_DB.setdefault(pivotLang, []).append(sentence);

for lang in possibleLanguages+[pivotLang]:
    newfilename = '%s.%s' %(outputPrefix, lang);
    random_utils.lines_to_file(newfilename, MULTI_DB[lang]);

