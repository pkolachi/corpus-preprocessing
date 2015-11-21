
import multiprocessing, re, sys, time;
from itertools import ifilter, imap, izip;
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
    if not mapping:
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

map_tag = defaultdict(lambda:'X');
def convert_tagged_text(*args):
    if len(args) < 1:
	print >>sys.stderr, "./%s <map-file>" %(sys.argv[0]);
	sys.exit(1);

    global map_tag;
    map_tag = read_mapping(args[0]);
    inputFileName  = args[1] if len(args) >= 2 else '';
    outputFileName = args[2] if len(args) >= 3 else '';
    outputFile = random_utils.smart_open(outputFileName, mode='wb');
    delimold = delimnew = '_';
    formsBuffer, tagsBuffer, bufferSize = [], [], 0;
    frst, scnd = itemgetter(0), itemgetter(1);

    keepTags = True;
    threads = 3;

    if threads > 1:
	pool = multiprocessing.Pool(threads, maxtasksperchild=1000);

    oldtime, newtime = time.time(), time.time();
    with random_utils.smart_open(outputFileName, mode='wb') as outputFile:
	for line in random_utils.lines_from_file(inputFileName):
	    tokens = [tuple(tok.rsplit(delimold, 1)) if tok.find(delimold) != -1 else (tok, '_UNK_') for tok in re.split('\s+', line.strip())];
	    current_forms = map(frst, tokens);
	    formsBuffer.append( current_forms );
	    if keepTags:
		current_tags = map(scnd, tokens);
		tagsBuffer.append( current_tags );
	    bufferSize += 1;
	    if bufferSize == 100000:
		if keepTags and threads > 1:
		    for current_forms, mapped_tags in izip(formsBuffer, pool.imap(convert, tagsBuffer, chunksize=10000)):
			print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
		elif keepTags and threads <= 1:
		    for current_forms, mapped_tags in izip(formsBuffer, imap(convert, tagsBuffer)):
			print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
		else:
		    for current_forms in formsBuffer:
			print >>outputFile, ' '.join(current_forms);
		formsBuffer, tagsBuffer, bufferSize = [], [], 0;
		newtime = time.time();
		print >>sys.stderr, "Dumping tags in %.5f"%(newtime-oldtime);
		oldtime = newtime;
	if bufferSize:
	    if keepTags and threads > 1:
		for current_forms, mapped_tags in izip(formsBuffer, pool.imap(convert, tagsBuffer, chunksize=10000)):
		    print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
	    elif keepTags and threads <= 1:
		for current_forms, mapped_tags in izip(formsBuffer, imap(convert, tagsBuffer)):
		    print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) for tok, tag in zip(current_forms, mapped_tags)]);
	    else:
		for current_forms in formsBuffer:
		    print >>outputFile, ' '.join(current_forms);
	    formsBuffer, tagsBuffer, bufferSize = [], [], 0;
	    newtime = time.time();
	    print >>sys.stderr, "Dumping tags in %.5f"%(newtime-oldtime);

    if threads > 1:
	pool.close();

    return;

if __name__ == '__main__':
    convert_tagged_text(sys.argv[1:]);
