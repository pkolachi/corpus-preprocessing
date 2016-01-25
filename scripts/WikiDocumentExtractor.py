#!/usr/bin/env python

from globalimports import *;
import random_utils;
import os;

import lxml.html as etree;
#import xml.etree.cElementTree as etree;
#from bs4 import BeautifulSoup;
import HTMLParser;

wikiextractdir = sysargv[1];
documentdir    = sysargv[2];

p = HTMLParser.HTMLParser();
for dirpath, dirsList, filesList in os.walk(wikiextractdir):
  for filename in filesList:
    filepath = os.path.join(dirpath, filename);
    print >>stderr, filepath;
    #with open(filepath) as infile:
    if 1:
      xmltree = etree.parse(filepath); 
      #xmltree = BeautifulSoup(infile, features="xml");
      xmlroot = xmltree.getroot();
      for docnode in xmlroot.findall('.//doc'):
        pageid = docnode.attrib['id'];
        pageurl = docnode.attrib['url'];
        pagetitle = docnode.attrib['title'];
        dirnum = int(pageid)/10000;
        dirname = str(dirnum).zfill(2);
        localdocumentdir = os.path.join(documentdir, dirname);
        if not os.path.isdir(localdocumentdir):
          os.makedirs(localdocumentdir);
        outputfilepath = os.path.join(localdocumentdir, 'wiki_%s' %pageid.zfill(6));
        with random_utils.smart_open(outputfilepath, 'w') as outfile:
          print >>outfile, p.unescape(etree.tostring(docnode, encoding='utf-8'));
        print >>stdout, "%s\t%s\t%s" %(pageid.zfill(6), pagetitle, pageurl);

