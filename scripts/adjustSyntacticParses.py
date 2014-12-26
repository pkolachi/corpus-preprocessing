
import sys;
import random_utils;

sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

def addEmptyParses(const_parses_file, empty_sent_ids):
    empty_sent_ids = dict([ (int(line.strip()), True) for line in random_utils.lines_from_file(empty_sent_ids) ]);
    sent_count = 0;
    for line in random_utils.lines_from_file(const_parses_file):
	sent_count += 1;
	while empty_sent_ids.has_key(sent_count):
	    print '(ROOT ())'
	    sent_count += 1;
	print line.strip();
    return;

def removeEmptyParses(const_parses_file, empty_sent_ids):
    empty_sent_ids = dict([ (int(line.strip()), True) for line in random_utils.lines_from_file(empty_sent_ids) ]);
    print >>sys.stderr, len(empty_sent_ids);
    sent_count = 0;
    tmp_count = 0;
    for line in random_utils.lines_from_file(const_parses_file):
	sent_count += 1;
	if empty_sent_ids.has_key(sent_count):
	    tmp_count += 1;
	    print line.strip();
    print >>sys.stderr, sent_count, tmp_count;
    return;

if __name__ == '__main__':
    const_parses_file, empty_sent_ids = sys.argv[1], sys.argv[2];
    #addEmptyParses(const_parses_file, empty_sent_ids);
    removeEmptyParses(const_parses_file, empty_sent_ids);
