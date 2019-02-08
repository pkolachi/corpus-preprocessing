#!/usr/bin/env python2

#from globalimports import *;
from globalimports import * ;
import random_utils as ru ;
import itertools as it ; 
import os;
from sys import stdout, stderr, stdin, argv as sysargv;
import io ;

wikiextractdir = sysargv[1];
documentdir    = sysargv[2];

k = 8 ; 
maxids = 10**k ; 
b = 4 ; 
bsize = 10**b ; 

filePaths = [] ; 
for dpth, dLs, fLs in os.walk(wikiextractdir):
  for fn in fLs:
    fpth = os.path.join(dpth, fn);
    filePaths.append(fpth) ; 

for fpth in sorted(filePaths) :
  print(fpth, file=stderr);
  docid = '' ;
  url   = '' ;
  title = '' ;
  buf = [] ;
  for line in ru.lines_from_file(fpth):
    if line.startswith('<doc '):
      if buf :
        # remove empty lines at begin and end
        #buf = [ln for ln in it.dropwhile(lambda X: not X.strip(), buf)] ; 
        #buf = [ln for ln in it.takewhile(lambda X: X.strip(), buf)] ; 
        # first line and last line should be specific <doc.* and </doc>
        buf = buf[1:]   if len(buf) and buf[0].startswith('<doc')  else buf ; 
        buf = buf[:-1]  if len(buf) and buf[-1].startswith('</doc') else buf ; 
        if len(buf) and len([l for l in buf if l.strip()]) : 
          ru.lines_to_file(ofpth, buf) ;
          print("{0}\t{1}\t{2}".format(docid.zfill(k), title, url), file=stdout) ;
        buf = [] ;
      
      fields  = re.findall('\"[^"]+?\"', line) ;
      docid   = fields[0][1:-1] ;
      url     = fields[1][1:-1] ;
      title   = fields[2][1:-1] ;
      dirnum  = int(int(docid)/bsize)+1 ;
      dirname = str(dirnum).zfill(b) ;
      localdocumentdir = os.path.join(documentdir, dirname) ;
      if not os.path.isdir(localdocumentdir):
        os.makedirs(localdocumentdir) ;
      ofpth = os.path.join(localdocumentdir, 'wiki_{0}'.format(docid.zfill(k))) ;
    buf.append(line) ;
  if buf:
    # remove empty lines at begin and end
    #buf = [ln for ln in it.dropwhile(lambda X: not X.strip(), buf)] ; 
    #buf = [ln for ln in it.takewhile(lambda X: X.strip(), buf)] ; 
    # first line and last line should be specific <doc.* and </doc>
    buf = buf[1:]   if len(buf) and buf[0].startswith('<doc')  else buf ; 
    buf = buf[:-1]  if len(buf) and buf[-1].startswith('</doc') else buf ; 
    if len(buf) and len([l for l in buf if l.strip()]) : 
      ru.lines_to_file(ofpth, buf) ;
      print("{0}\t{1}\t{2}".format(docid.zfill(k), title, url), file=stdout) ;
    buf = [] ;
