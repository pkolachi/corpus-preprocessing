#!/usr/bin/env python3

"""
A script to run a command/script on all files in a given directory
You can simulate this using a combination of xargs + diff -dir
"""

import os, sys;

source_directory, target_directory = sys.argv[1], sys.argv[2];
source_directory = os.path.abspath(source_directory);
target_directory = os.path.abspath(target_directory);
#source_directory, target_directory, target_directory2 = sys.argv[1], sys.argv[2], sys.argv[3];
#source_directory, target_directory, target_directory2 = os.path.abspath(source_directory), os.path.abspath(target_directory), os.path.abspath(target_directory2);

for dirpath, dirsList, filesList in os.walk(source_directory):
  for filename in filesList:
    filepath = os.path.join(dirpath, filename);	
	#outfilename = filename;
	outfilename = os.path.splitext(filename)[0]+'.conll';
	#outfilename = os.path.splitext(filename)[0]+'.tok';
	outfilepath = os.path.join(dirpath.replace(source_directory, \
		target_directory), outfilename);
	#outfilepath2 = os.path.join(dirpath.replace(source_directory, \
	#       target_directory2), outfilename);
	
	print filepath, outfilepath;
	
	#runCmd = 'pypy wiki_deprels_utils.py %s %s %s' %(filepath, outfilepath, outfilepath2);
	#runCmd = 'pypy stanforddependencyconverter.py %s > %s' %(filepath, outfilepath);
	#runCmd = 'python stanford_corenlp_utils.py %s %s' %(filepath, outfilepath));
	runCmd = 'pypy conll_utils.py < %s > %s 2> /dev/null' %(filepath, outfilepath));
	runCmd = 'sh /Users/prakol/Documents/chalmers-work/gf-translation/translator-benchmarking/scripts/ptbTok2gfTok.sh < %s > %s 2> /dev/null' %(filepath, outfilepath));
	
	if os.system(runCmd):
      print >>sys.stderr, filepath; 
  
  for dirname in dirsList:
    fulldirpath = os.path.join(dirpath, dirname);
    outdirpath = fulldirpath.replace(source_directory, target_directory);
    if not os.path.isdir(outdirpath):
      os.makedirs(outdirpath);
    #outdirpath = fulldirpath.replace(source_directory, target_directory2);
    #if not os.path.isdir(outdirpath):
    #  os.makedirs(outdirpath);
