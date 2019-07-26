#!/usr/bin/env python2

#from globalimports import *;
import random_utils as ru ;
import os;
from sys import stdout, stderr, stdin, argv as sysargv;
import lxml.html as etree;
import io ;
#import xml.etree.cElementTree as etree;
#from bs4 import BeautifulSoup;
from html.parser import HTMLParser;
#from html import unescape ; 
from xml.sax.saxutils import unescape as unescape ; 

wikiextractdir = sysargv[1];
documentdir    = sysargv[2];

p = HTMLParser();
for dirpath, dirsList, filesList in os.walk(wikiextractdir):
  for filename in filesList:
    filepath = os.path.join(dirpath, filename);
    print(filepath, file=stderr);
    #with open(filepath) as infile:
    if 1:
      xmltree = etree.parse(filepath); 
      #xmltree = BeautifulSoup(infile, features="xml");
      xmlroot = xmltree.getroot();
      for docnode in xmlroot.findall('.//doc'):
        pageid = docnode.attrib['id'];
        pageurl = docnode.attrib['url'];
        pagetitle = docnode.attrib['title'];
        dirnum = int(int(pageid)/10000);
        dirname = str(dirnum).zfill(2);
        localdocumentdir = os.path.join(documentdir, dirname);
        if not os.path.isdir(localdocumentdir):
          os.makedirs(localdocumentdir);
        outputfilepath = os.path.join(localdocumentdir, 'wiki_%s' %pageid.zfill(6));
        content = etree.tostring(docnode, method='text', encoding='unicode');
        print(type(content));
        content = unescape(content);
        content = content.split('\n') ; 
        if content:
          content = content[1:-1] ;
        content = '\n'.join(content) ;
        print(type(content));
        with io.open(outputfilepath, 'w', encoding='utf-8') as outfile:
          outfile.write(content);
        print("{0}\t{1}\t{2}".format(pageid.zfill(6), pagetitle, pageurl), file=stdout);

