
import itertools, multiprocessing, os, os.path, re, string, sys, time;
from operator import itemgetter;
import random_utils;

def read_mapping(mapfile):
    map_tags = {};
    for line in random_utils.lines_from_file(mapfile):
	line = line.strip();
	fine, coarse = line.split('\t');
	fine = (fine, ) if fine.find('|') == -1 else tuple(fine.split('|'));
	map_tags[fine] = coarse;
    return map_tags;

def convert(tag_sequence, mapping=None):
    global map_tag;
    mapping = map_tag;
    coarse_sequence = [];
    for idx, tag in enumerate(tag_sequence):
	possible_matches = filter(lambda X: X[0] == tag, mapping.keys());
	if len(possible_matches) > 1 and idx > 0:
	    best_match = filter(lambda X: X[1] == tag_sequence[idx-1], filter(lambda X: len(X) == 2, possible_matches) );
	    if len(best_match) < 1: best_match = filter(lambda X: len(X) == 1, possible_matches);
	    coarse_sequence.append( mapping[best_match[0]] );
	elif tag == '_UNK_' or len(possible_matches) == 0:
	    coarse_sequence.append( 'X' );
	else:
	    coarse_sequence.append( mapping[possible_matches[0]] );
    return coarse_sequence;

map_tag = {};
def convert_tagged_text(*args):
    if len(args) < 1:
	print >>sys.stderr, "./%s <map-file>" %(sys.argv[0]);
	sys.exit(1);

    global map_tag;
    map_tag = read_mapping(args[0]);
    inputFileName  = args[1] if len(args) >= 2 else '';
    outputFileName = args[2] if len(args) >= 3 else '';
    outputFile = smart_open(outputFileName, mode='w');
    delimold = delimnew = '_';
    formsBuffer, tagsBuffer, bufferSize = [], [], 0;

    pool = multiprocessing.Pool(4, maxtasksperchild=1000);

    oldtime, newtime = time.time(), time.time();
    for line in random_utils.lines_from_file(inputFileName):
	tokens = [tuple(tok.rsplit(delimold, 1)) if tok.find(delimold) != -1 else (tok, '_UNK_') for tok in re.split('\s+', line.strip())];
	current_forms = map(itemgetter(0), tokens);
	formsBuffer.append( current_forms );
	current_tags  = [  ( '_UNK_' if tok.find(delimold) == -1 else tok.rsplit(delimold, 1)[1] ) for tok in tokens  ];
	current_tags = map(itemgetter(1), tokens);
	tagsBuffer.append( current_tags );
	bufferSize += 1; 
	if bufferSize == 100000:
	    for current_forms, mapped_tags in itertools.izip(formsBuffer, pool.imap(convert, tagsBuffer, chunksize=10000)):
	    	print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
	    #for current_forms in formsBuffer:
	    #	print >>outputFile, ' '.join(current_forms);
	    formsBuffer, tagsBuffer, bufferSize = [], [], 0;
	    newtime = time.time();
	    print >>sys.stderr, "Dumping tags in %.5f"%(newtime-oldtime);
	    oldtime = newtime;
    if bufferSize:
	for current_forms, mapped_tags in itertools.izip(formsBuffer, pool.imap(convert, tagsBuffer, chunksize=10000)):
	    print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
	for current_forms in formsBuffer:
	    print >>outputFile, ' '.join(current_forms);
	formsBuffer, tagsBuffer, bufferSize = [], [], 0;
	newtime = time.time();
	print >>sys.stderr, "Dumping tags in %.5f"%(newtime-oldtime);

    pool.close();
    return;

if __name__ == '__main__':
    convert_tagged_text(sys.argv[1:]);
