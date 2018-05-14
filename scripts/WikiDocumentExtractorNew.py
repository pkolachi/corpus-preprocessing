#!/usr/bin/env python2

#from globalimports import *;
from globalimports import * ;
import random_utils as ru ;
import os;
from sys import stdout, stderr, stdin, argv as sysargv;
import io ;

wikiextractdir = sysargv[1];
documentdir    = sysargv[2];

for dirpath, dirsList, filesList in os.walk(wikiextractdir):
  for filename in filesList:
    filepath = os.path.join(dirpath, filename);
    print(filepath, file=stderr);
    docid = '' ;
    url   = '' ;
    title = '' ;
    buf = [] ;
    for line in ru.lines_from_file(filepath):
      if line.startswith('<doc'):
        if buf:
          buf = buf[1:-1] ;
          ru.lines_to_file(outfilepath, buf) ;
          buf = [] ;
          print("{0}\t{1}\t{2}".format(docid.zfill(6), title, url), file=stdout) ;

        fields = re.findall('\"[^"]+?\"', line) ;
        docid  = fields[0][1:-1] ;
        url    = fields[1][1:-1] ;
        title  = fields[2][1:-1] ;

        dirnum = int(int(docid)/10000) ;
        dirname = str(dirnum).zfill(2) ;
        localdocumentdir = os.path.join(documentdir, dirname) ;
        if not os.path.isdir(localdocumentdir):
          os.makedirs(localdocumentdir) ;
        outfilepath = os.path.join(localdocumentdir, 'wiki_{0}'.format(docid.zfill(6))) ;
      buf.append(line) ;

    if buf:
      buf = buf[1:-1] ;
      content = '\n'.join(buf) ;
      ru.lines_to_file(outfilepath, content) ;
      buf = [] ;

