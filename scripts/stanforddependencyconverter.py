#!/usr/bin/env python3

from __future__ import print_function;

import shlex, subprocess, os, sys;
from multiprocessing import cpu_count;
try:
  import random_utils;
except ImportError:
  print("Missing necessary module 'random_utils'", file=sys.stderr);
  sys.exit(1);

#stanford_parser_dir = '/Users/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-10-31';
#stanford_parser_dir = '/Users/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2013-11-12';
#stanford_parser_dir = '/Users/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2015-04-20';
stanford_parser_dir = '/home/prakol/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2015-12-09';

dep_conversion_cmd = '''
/home/prakol/Documents/softwares/java/jre1.8.0_40/bin/java -mx3000m -cp "%s/*:" edu.stanford.nlp.trees.EnglishGrammaticalStructure \
    -basic \
    -keepPunct \
    -conllx \
    -nthreads %d \
    -treeFile ''' %(stanford_parser_dir, cpu_count());
#dep_conversion_cmd = '''
#/home/prakol/Documents/softwares/java/jre1.8.0_40/bin/java -mx3000m -cp "%s/*:" edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure \
#    -basic \
#    -keepPunct \
#    -conllx \
#    -nthreads %d \
#    -treeFile ''' %(stanford_parser_dir, cpu_count());

const_parse_file = sys.argv[1];
tmpfile = '/tmp/%s.pid' %(os.getpid());
parsesBuf = [];
fnull = open(os.devnull, 'w');
for parse in random_utils.lines_from_file(const_parse_file):
  parsesBuf.append(parse.strip());
  if len(parsesBuf) > 100000:
    random_utils.lines_to_file(tmpfile, parsesBuf);
    cmd = '%s %s' %(dep_conversion_cmd, tmpfile);
    if subprocess.call(shlex.split(cmd), stdout=sys.stdout, stderr=sys.stderr) != 0:
      sys.exit(1);
    parsesBuf = [];
if len(parsesBuf):
  random_utils.lines_to_file(tmpfile, parsesBuf);
  cmd = '%s %s' %(dep_conversion_cmd, tmpfile);
  if subprocess.call(shlex.split(cmd), stdout=sys.stdout, stderr=sys.stderr) != 0:
    sys.exit(1);
  parsesBuf = [];

