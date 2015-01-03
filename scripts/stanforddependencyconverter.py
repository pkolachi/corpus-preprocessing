
import codecs, multiprocessing, shlex, subprocess, os, sys;
try:
    import random_utils;
except ImportError:
    print >>sys.stderr, "Missing necessary module 'random_utils'";
    sys.exit(1);

stanford_parser_dir = '/Users/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-10-31';
#stanford_parser_dir = '/Users/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2013-11-12';

dep_conversion_cmd = 'java -mx3000m -cp "%s/*:" edu.stanford.nlp.trees.EnglishGrammaticalStructure -basic -keepPunct -conllx -nthreads %d -treeFile' %(stanford_parser_dir, multiprocessing.cpu_count());

const_parse_file = sys.argv[1];
tmpfile = '/tmp/%s.pid' %(os.getpid());
tmpParsesCache, parseIdx = [], 0;
fnull = open(os.devnull, 'w');
for parse in random_utils.lines_from_file(const_parse_file):
    parseIdx += 1;
    tmpParsesCache.append(parse.strip());
    if not parseIdx%100000:
	random_utils.lines_to_file(tmpfile, tmpParsesCache);
	cmd = '%s %s' %(dep_conversion_cmd, tmpfile);
	if subprocess.call(shlex.split(cmd), stdout=sys.stdout, stderr=fnull) != 0:
	    sys.exit(1);
	tmpParsesCache = [];
if len(tmpParsesCache):
    random_utils.lines_to_file(tmpfile, tmpParsesCache);
    cmd = '%s %s' %(dep_conversion_cmd, tmpfile);
    if subprocess.call(shlex.split(cmd), stdout=sys.stdout, stderr=fnull) != 0:
	sys.exit(1);
    tmpParsesCache = [];
