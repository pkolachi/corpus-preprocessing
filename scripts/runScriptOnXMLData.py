
import codecs, os, shlex, string, subprocess, sys;
#import lxml.etree as etree;
import xml.etree.cElementTree as etree;

def convertXMLTexttoRaw(text):
    for key, value in {'&apos;': "'", '&amp;': "&", '&lt;': "<", '&gt;': ">"}.iteritems():
	text = text.replace(key, value);
    return text;

def extractRawData(doc):
    root = doc.getroot();
    data_nodes = [];
    for subtree in root.iter():
	if subtree.text != None and (subtree.text.strip() and subtree.text.strip() not in string.punctuation):
	    data_nodes.append( (subtree, subtree.text.strip().split('\n')) );
    return data_nodes;

def runScript(scriptName, inputfileArg, outputfileArg, *args):
    processing_cmd = 'sh %s %s %s %s' %(scriptName, inputfileArg, outputfileArg, ' '.join(args));
    return True if (subprocess.call(shlex.split(processing_cmd)) == 0) else False;

def main():
    if len(sys.argv) < 3:
	print >>sys.stderr, "./runScriptOnXMLData.py script-name xml-file *args";
	sys.exit(1);

    scriptName = sys.argv[1];
    xmlFile = sys.argv[2];
    args = sys.argv[3:];
    print >>sys.stderr, "'%s'\t%s\t%s" %(scriptName, xmlFile, repr(args)); 
    #parser = etree.XMLParser(encoding="utf-8");
    doc = etree.parse(xmlFile);
    text_contents = extractRawData(doc);
    if scriptName.strip():
	tmpinfile, tmpoutfile = '/tmp/%s.%s.in'%(os.getpid(), scriptName), '/tmp/%s.%s.out' %(os.getpid(), scriptName);
	print >>sys.stderr, tmpinfile, tmpoutfile;
	tmpout = codecs.open(tmpinfile, 'w', 'utf-8');
    else:
	print >>sys.stderr, "No script name: writing raw contents to STDOUT";
	tmpout = codecs.getwriter('utf-8')(sys.stdout);
    for node, lines in text_contents:
	print >>tmpout, '\n'.join(lines);

    #if runScript(scriptName, tmpinfile, tmpoutfile, args):
	#with codecs.open(tmpoutfile, 'r', 'utf-8') as tmpinfile:
	    #for line, (node, text) in zip(tmpinfile, text_contents.iteritems()):


if __name__ == '__main__':
    main();
    
