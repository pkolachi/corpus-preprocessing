#!/usr/bin/env python3

from __future__ import print_function;

import os, sys;
try:
  from itertools import imap as map, izip as zip, ifilter as filter, repeat;
except ImportError:
  from itertools import repeat;
import multiprocessing as Threads;

srcDirectory = sys.argv[1];
tgtDirectory = sys.argv[2];
srcDirectory = os.path.abspath(srcDirectory)
tgtDirectory = os.path.abspath(tgtDirectory);

cmpFilesList = [];

for dirpath, dirList, fileList in os.walk(srcDirectory):
  tgtdirpath = dirpath.replace(srcDirectory, tgtDirectory);
  tgtdirsList = map(os.path.join, repeat(tgtdirpath, len(dirList)), \
      (dirname.replace(srcDirectory, tgtDirectory) for dirname in dirList));
  for tgtdir in tgtdirsList:
    if os.path.isdir(tgtdir) == False:
      print("%s: Target directory does not exist" %(tgtdir));
    
  tgtfilesList = map(os.path.join, repeat(tgtdirpath, len(fileList)), \
      (filename.replace(srcDirectory, tgtDirectory) for filename in fileList));
  srcfileList = map(os.path.join, repeat(dirpath, len(fileList)), fileList);
  cmpFilesList.extend([(srcfile, tgtfile) for srcfile, tgtfile in zip(srcfileList, tgtfilesList)]);

def Compare(args):
  srcfile, tgtfile = args;
  #print(srcfile+", "+tgtfile, file=sys.stderr);
  if os.path.isfile(tgtfile) == False:
    return "%s: Target file does not exist" %(tgtfile);
  elif os.system('cmp "%s" "%s" > /dev/null 2> /dev/null' %(srcfile, tgtfile)) != 0:
    return "%s: Target file does not match" %(tgtfile);
  else:
    return "";

#pool = Threads.Pool(8);
#cmpOutput = pool.map(Compare, cmpFilesList, chunksize=10000);
#pool.close();
#pool.join();

cmpOutput = map(Compare, cmpFilesList);
cmpOutput = filter(None, cmpOutput);
print("\n".join(cmpOutput));
