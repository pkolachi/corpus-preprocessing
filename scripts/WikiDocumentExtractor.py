
import codecs, os, sys;
import lxml.html as etree;
#import xml.etree.cElementTree as etree;
#from bs4 import BeautifulSoup;

wikiextractdir, documentdir = sys.argv[1], sys.argv[2];

sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

for dirpath, dirsList, filesList in os.walk(wikiextractdir):
    for filename in filesList:
	filepath = os.path.join(dirpath, filename);
	print >>sys.stderr, filepath;
	xmltree = etree.parse(filepath); # BeautifulSoup(infile, features="xml");
	xmlroot = xmltree.getroot();
	for docnode in xmlroot.findall('.//doc'):
	    pageid, pageurl, pagetitle = docnode.attrib['id'], docnode.attrib['url'], docnode.attrib['title'];
	    dirnum = int(pageid)/10000;
	    dirname = str(dirnum).zfill(2);
	    localdocumentdir = os.path.join(documentdir, dirname);
	    if not os.path.isdir(localdocumentdir):
		os.makedirs(localdocumentdir);
	    outputfilepath = os.path.join(localdocumentdir, 'wiki_%s' %pageid.zfill(6));
	    with codecs.open(outputfilepath, 'w', 'utf-8') as outfile:
		print >>outfile, docnode.text;
	    print "%s\t%s\t%s" %(pageid.zfill(6), pagetitle, pageurl);
