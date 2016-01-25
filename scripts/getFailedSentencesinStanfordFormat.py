#!/usr/bin/env python

import codecs, sys;
try:
    import conll_utils;
    import random_utils;
except ImportError:
    print >>sys.stderr, "Missing necessary module 'random_utils' and 'conll_utils'";
    sys.exit(1);

sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

def convertToStanfordTagged(conll_sentence):
    tokens = [];
    for entry in conll_sentence:
	tokens.append('%s_%s' %(entry['form'], entry['cpostag']) );
    return ' '.join(tokens);

def getFailedSentencesinStanfordFormat(const_parse_file, dep_parse_file):
    with codecs.open(const_parse_file, 'r', 'utf-8') as infile:
	depParseList = conll_utils.sentences_from_conll( codecs.open(dep_parse_file, 'r', 'utf-8') );
	idx = 0;
	for line in infile:
	    idx += 1;
	    if line.strip() in ['(())', 'NONE', '(ROOT ())', '(ROOT())', '(S1 ())']:
		tagged_string = convertToStanfordTagged( depParseList.next() );
		print "%d\t%s" %(idx, tagged_string);
	    else:
		depParseList.next();

def replaceMissingParses(berkeley_parse_file, stanford_parse_file):
    stanfordParses = {};
    with codecs.open(stanford_parse_file, 'r', 'utf-8') as stanfordparseList:
	for line in stanfordparseList:
	    sid, stanford_parse = line.strip().split('\t');
	    sid = int(sid);
	    stanfordParses[sid] = stanford_parse.strip();
    with codecs.open(berkeley_parse_file, 'r', 'utf-8') as berkeleyparseList:
	    berkeleyParseIdx = 0;
	    for berkeley_parse in berkeleyparseList:
		berkeleyParseIdx += 1;
		if stanfordParses.has_key(berkeleyParseIdx):
		    try: assert( berkeley_parse.strip() in ['(())', 'NONE', '(ROOT ())', '(ROOT())', '(S1 ())'] );
		    except AssertionError: print >>sys.stderr, berkeleyParseIdx, berkeley_parse.strip(); sys.exit(1);
		    print stanfordParses[berkeleyParseIdx];
		else:
		    print berkeley_parse.strip();


#const_parse_file, dep_parse_file = sys.argv[1], sys.argv[2];
#getFailedSentencesinStanfordFormat(const_parse_file, dep_parse_file);
berkeley_parse_file, stanford_parse_file = sys.argv[1], sys.argv[2];
replaceMissingParses(berkeley_parse_file, stanford_parse_file);
