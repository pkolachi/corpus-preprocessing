
import itertools, operator;
from collections import defaultdict;
import random_utils;

def prepareVcb(corpusfilename):
    outfilename = '%s.snt' %(corpusfilename);
    
    vocabulary = {'UNK': 1};
    vocab_idgen = itertools.count(2);
    frequencies = defaultdict(lambda: 0);
    with random_utils.smart_open(outfilename, 'w') as outfile:
	for line in random_utils.lines_from_file(corpusfilename):
	    encline = random_utils.encode_sentence(line.strip(), vocabulary, vocab_idgen);
	    for tokenid in encline:
		frequencies[tokenid] += 1;
	    print >>outfile, " ".join(str(tokenid) for tokenid in encline);

    if outfilename != '':
	vcbfilename = '%s.vcb' %(outfilename);
	with random_utils.smart_open(vcbfilename, 'w') as outfile:
	    for word, wordidx in sorted(vocabulary.iteritems(), key=operator.itemgetter(1)):
		print >>outfile, "%d %s %d" %(wordidx, word, frequencies[wordidx]);
    
    return;

