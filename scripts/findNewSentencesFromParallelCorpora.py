#!/usr/bin/env python

import codecs, itertools, os.path, sys;
import random_utils;

if len(sys.argv) != 6:
    print >>sys.stderr, "Error: ./%s <src-file> <tgt-file> <output-prefix>"%(sys.argv[0]);
    sys.exit(1);

srcfilename, tgtfilename = sys.argv[1], sys.argv[2];
srcext, tgtext = os.path.splitext(srcfilename)[1], os.path.splitext(tgtfilename)[1];
srctext, tgttext = {}, {};
srcvocab, tgtvocab = {}, {};
srcvocab_idgen, tgtvocab_idgen = itertools.count(1), itertools.count(1);
parallelDB = {};
line_count = 0;
for srcline, tgtline in itertools.izip(\
	random_utils.lines_from_file(srcfile), \
	random_utils.lines_from_file(tgtfile) ):
    line_count += 1;
    if srcline.strip() == '' or tgtline.strip() == '':
	continue;
    srcline = tuple( random_utils.encode_sentence(srcline.strip(), srcvocab, srcvocab_idgen) );
    tgtline = tuple( random_utils.encode_sentence(tgtline.strip(), tgtvocab, tgtvocab_idgen) );
    if parallelDB.has_key(srcline) and parallelDB[srcline].has_key(tgtline):
	continue;
    else:
	parallelDB.setdefault(srcline, {})[tgtline] = line_count;

newsrcfilename, newtgtfilename = sys.argv[3], sys.argv[4];
outputfileprefix = sys.argv[5];
with codecs.open('%s%s' %(outputfileprefix, srcext), 'w', 'utf-8') as srcoutfile:
    with codecs.open('%s%s' %(outputfileprefix, tgtext), 'w', 'utf-8') as tgtoutfile:
	for srcline, tgtline in itertools.izip(\
		random_utils.lines_from_file(newsrcfilename), \
		random_utils.lines_from_file(newtgtfilename) ):
	    encsrcline = tuple( random_utils.encode_sentence(srcline.strip(), srcvocab, srcvocab_idgen) );
	    enctgtline = tuple( random_utils.encode_sentence(tgtline.strip(), tgtvocab, tgtvocab_idgen) );
	    if not (parallelDB.has_key(encsrcline) and parallelDB[encsrcline].has_key(enctgtline)):
		print >>srcoutfile, srcline.strip();
		print >>tgtoutfile, tgtline.strip();
