
import multiprocessing, re, sys, time;
#from itertools import ifilter as filter, imap as map, izip as zip;
try:
    from itertools import ifilter as filter, imap as imap, izip_longest as zip, islice, tee;
except ImportError:
    # implies this is Python 3.
    pass;
from collections import defaultdict;
from operator import itemgetter;
import random_utils, parallelize_utils;

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
        possible_matches = list(filter(lambda X: X[0] == tag, mapping.keys()));
        if len(possible_matches) > 1 and idx > 0:
            best_match = list( filter(lambda X: X[1] == tag_sequence[idx-1], \
		    filter(lambda X: len(X) == 2, possible_matches) ) );
            if len(best_match) < 1: 
                best_match = filter(lambda X: len(X) == 1, possible_matches);
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
    delimold = delimnew = '_';
    bufsize = 500000;
    frst, scnd = itemgetter(0), itemgetter(1);

    keepTags = True;
    threads = 2;

    oldtime, newtime = time.time(), time.time();
    with random_utils.smart_open(outputFileName, mode='wb') as outputFile:
        sentences = imap(lambda line: [tuple(tok.rsplit(delimold, 1)) \
                if tok.find(delimold) != -1 \
                else (tok, '_UNK_') \
                for tok in re.split('\s+', line.strip())], 
                random_utils.lines_from_file(inputFileName) );
        while True:
            sentences_buf = list(islice(sentences, bufsize));
            tokenized_sentences = imap(lambda x: map(frst, x), sentences_buf);
            tagged_sentences    = imap(lambda x: map(scnd, x), sentences_buf);
            if not keepTags:
                for current_forms in tokenized_sentences:
                    print >>outputFile, ' '.join(current_forms);
            elif keepTags and threads <= 1:
                mapper = imap(convert, tagged_sentences);
                for current_forms, mapped_tags in zip(tokenized_sentences, mapper):
                    print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) \
			for tok, tag in zip(current_forms, mapped_tags)]);
            elif keepTags and threads > 1:
                mapper = parallelize_utils.parimap(convert, tagged_sentences, \
		    workers=threads, chunksize=10000); 
                for current_forms, mapped_tags in zip(tokenized_sentences, mapper):
                    print >>outputFile, ' '.join(['%s%c%s'%(tok, delimnew, tag) \
			for tok, tag in zip(current_forms, mapped_tags)]);
            if len(sentences_buf) < bufsize:
                break;
    return;

if __name__ == '__main__':
    convert_tagged_text(*sys.argv[1:]);
