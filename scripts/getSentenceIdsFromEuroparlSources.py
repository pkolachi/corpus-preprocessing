
import codecs, itertools, re, sys;
import random_utils;
#import nltk.tokenize;

def getMappingBetweenTwoFiles(source_file, subset_file):
    vocabulary, vocab_idgen = {}, itertools.count(1);
    with codecs.open(source_file, 'r', 'utf-8') as infile:
	source_sentences, line_count = {}, 0;
	inv_source_sentences = {};
	for line in infile:
	    line_count += 1;
	    if not (line_count%500000): print >>sys.stderr, '.',
	    if line.strip() == '':
		continue;
	    #num_repr = random_utils.encode_sentence(' '.join(nltk.tokenize.word_tokenize(line.strip())), vocabulary, vocab_idgen);
	    num_repr = random_utils.encode_sentence(' '.join(re.split('(\W+)', line.strip())), vocabulary, vocab_idgen);
	    #source_sentences[sent_idx] = num_repr;
	    inv_source_sentences.setdefault(repr(num_repr), []).append(line_count);
	print >>sys.stderr, line_count;

    with codecs.open(subset_file, 'r', 'utf-8') as infile:
	line_count = 0;
	needle_idx, prev_needle_idx = 0, 0;
	for line in infile:
	    line_count += 1;
	    if not (line_count%500000): print >>sys.stderr, '.',
	    if line.strip() == '': 
		print '%d: None' %(line_count);
	    else:
		num_repr = random_utils.encode_sentence(' '.join(re.split('(\W+)', line.strip())), vocabulary, vocab_idgen);
		if not inv_source_sentences.has_key(repr(num_repr)):
		    needle_idx = -1;
		else:
		    if len(inv_source_sentences[repr(num_repr)]) > 1:
			for idx in inv_source_sentences[repr(num_repr)]:
			    if idx < prev_needle_idx:
				continue;
			    needle_idx = idx;
			    break;
		    else:
			needle_idx = inv_source_sentences[repr(num_repr)][0];
		    prev_needle_idx = needle_idx;
		#print "%d: %d" %(line_count, needle_idx);
		if needle_idx == -1: print "%d: %d" %(line_count, needle_idx) 
		else:                print "%d: %s" %(line_count, ",".join([str(match) for match in inv_source_sentences[repr(num_repr)]]));
	print >>sys.stderr, line_count;
    return;
    
source_file, subset_file = sys.argv[1], sys.argv[2];
getMappingBetweenTwoFiles(source_file, subset_file);
