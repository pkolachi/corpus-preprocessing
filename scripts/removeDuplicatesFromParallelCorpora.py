
import codecs, itertools, os.path, sys;
import random_utils;

if len(sys.argv) != 4:
    print >>sys.stderr, "Error: ./%s <src-file> <tgt-file> <output-prefix>";
    sys.exit(1);

srcfilename, tgtfilename = sys.argv[1], sys.argv[2];
srcext, tgtext = os.path.splitext(srcfilename)[1], os.path.splitext(tgtfilename)[1];
srcSegments, tgtSegments = {}, {};
srcvocab, tgtvocab = {}, {};
srcvocab_idgen, tgtvocab_idgen = itertools.count(1), itertools.count(1);
srcEncSegments, tgtEncSegments = {}, {};
line_count = 0;
for srcline, tgtline in itertools.izip(\
	random_utils.lines_from_file(srcfilename), \
	random_utils.lines_from_file(tgtfilename) ):
    line_count += 1;
    if srcline.strip() == '' or tgtline.strip() == '':
	continue;
    srcSegments[line_count] = srcline.strip();
    tgtSegments[line_count] = tgtline.strip();
    srcline = random_utils.encode_sentence(srcline.strip(), srcvocab, srcvocab_idgen);
    tgtline = random_utils.encode_sentence(tgtline.strip(), tgtvocab, tgtvocab_idgen);
    if srcEncSegments.has_key(srcline) and tgtEncSegments.has_key(tgtline):
	continue;
    else:
	srcEncSegments[srcline] = line_count;
	tgtEncSegments[tgtline] = line_count;

outputfileprefix = sys.argv[3];
final_items = sorted(srcEncSegments.values());
random_utils.lines_to_file('%s%s' %(outputfileprefix, srcext), (srcSegments.get(idx, "") for idx in final_items));
random_utils.lines_to_file('%s%s' %(outputfileprefix, tgtext), (tgtSegments.get(idx, "") for idx in final_items));
