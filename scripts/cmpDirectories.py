#!/usr/bin/env python3

from __future__ import print_function;

import os, sys;
try:
  from itertools import imap as map, izip as zip, ifilter as filter, repeat;
except ImportError:
  from itertools import repeat;

srcDirectory = sys.argv[1];
tgtDirectory = sys.argv[2];
srcDirectory = os.path.normpath(srcDirectory)
tgtDirectory = os.path.normpath(tgtDirectory);

for dirpath, dirList, fileList in os.walk(srcDirectory):
  tgtdirpath = dirpath.replace(srcDirectory, tgtDirectory);
  tgtdirsList = map(os.path.join, repeat(tgtdirpath, len(dirList)), \
      (dirname.replace(srcDirectory, tgtDirectory) for dirname in dirList));
  for tgtdir in tgtdirsList:
    if os.path.isdir(tgtdir) == False:
      print("%s: Target directory does not match" %(tgtdir));
    
  tgtfilesList = map(os.path.join, repeat(tgtdirpath, len(fileList)), \
      (filename.replace(srcDirectory, tgtDirectory) for filename in fileList));
  srcfileList = map(os.path.join, repeat(dirpath, len(fileList)), fileList);
  for srcfile, tgtfile in zip(srcfileList, tgtfilesList):
    if os.path.isfile(tgtfile) == False or \
        os.system('cmp "%s" "%s" > /dev/null 2> /dev/null' %(srcfile, tgtfile)) != 0:
          print("%s: Target file does not match" %(tgtfile));
