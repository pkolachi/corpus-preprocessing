
import codecs, multiprocessing, os, os.path, random, re, shlex, string, subprocess, sys;
from math import log10;
try:
    import random_utils;
    import lxml.etree as etree;
except ImportError:
    print >>sys.stderr, "Missing random_utils module."
    import xml.etree.cElementTree as etree; #incompatible due to pretty_print functionality of writing xml
#import xml.etree.ElementTree as etree;  #same reason as above

sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

def sortFileNamesByNumber(filesList):
    sortKeys = {};
    for filepath in filesList:
	filename = os.path.split(filepath)[1];
	try:
	    #sortKeys[int(filename.split('.', 1)[0])] = filepath;
	    sortKeys[int(filename.rsplit('.', 2)[1])] = filepath;
	except ValueError:
	    yield filepath
    for key in sorted(sortKeys.keys()):
	yield sortKeys[key];

def addTwoXMLDocuments(doc1, doc2, elem_attr):
    #doc1, doc2 = lxml.etree.parse(xml_file1), lxml.etree.parse(xml_file2);
    root1, root2 = doc1.getroot(), doc2.getroot();

    # manipulation of 'sentence' elements inside XML
    #root1.addChildList( root2.children.copyNodeList() );
    root1_mainNode = root1.find(".//sentences");
    sent_attr_in_doc1 = {};
    if elem_attr['id'] == '0':
	for sent_node in root1.findall(".//sentence"):
	    sent_attr_in_doc1 = sent_node.attrib;
	elem_attr.update(sent_attr_in_doc1);
    else:
	sent_attr_in_doc1 = elem_attr;

    for sent_node in root2.findall(".//sentence"):
	sent_node.attrib['id'] = repr( int(sent_node.attrib['id'])+int(sent_attr_in_doc1['id']) );
	sent_node.attrib['line'] = repr( int(sent_node.attrib['line'])+int(sent_attr_in_doc1['line']) );
	root1_mainNode.append(sent_node);
    elem_attr.update(sent_node.attrib);

    # end of manipulating doc, return element
    return doc1;

def mergeSegementedCoreNLPOutput(xmlfiles):
    idx = 0;
    doc, elem_attr = None, {'id': '0', 'line': '0'};
    for xmlfile in sortFileNamesByNumber(xmlfiles):
	print >>sys.stderr, xmlfile;
	if idx == 0:
	    doc = etree.parse(xmlfile);
	else:
	    new_doc = etree.parse(xmlfile);
	    doc = addTwoXMLDocuments(doc, new_doc, elem_attr);
	    del new_doc;
	idx += 1;
    print etree.tostring(doc.getroot(), encoding='utf-8', method='xml');
    #print writeXMLFile(sys.argv[1], mergedDoc);
    return;

def splitCoreNLPOutputForSentences(doc, outputDirectory, elem_attr):
    root = doc.getroot();
    root_mainNode = root.find(".//sentences");
    sentences = root.findall(".//sentence");
    # remove all sentences from the xml content
    for sent in sentences: 
	root_mainNode.remove(sent);
    sent_node = None;
    for sent_node in sentences:
	sent_node.attrib['id'] = repr( int(sent_node.attrib['id'])+int(elem_attr['id']) );
	sent_node.attrib['line'] = repr( int(sent_node.attrib['line'])+int(elem_attr['line']) );
	root_mainNode.append(sent_node);
	outputFileName = os.path.join(outputDirectory, '%s.xml' %(sent_node.attrib['id']));
	mod_doc = etree.ElementTree(root_mainNode);
	mod_doc.write(outputFileName, encoding='utf-8', method='xml');
	root_mainNode.remove(sent_node);
    if sent_node != None:
	elem_attr.update(sent_node.attrib);
    return;

def splitCoreNLPOutputForWiki(doc, outputDirectory, elem_attr):
    # small lambda functions to deal especially with wiki 
    import re;
    first_token  = lambda sentence_node: sentence_node.find(".//token").find("word").text;
    second_token = lambda sentence_node: sentence_node.findall(".//token")[1].find("word").text \
	    if len(sentence_node.findall(".//token")) > 1 else 'MySpecialNone';
    wiki_header = lambda raw_token: raw_token.startswith('<doc') and raw_token.endswith('>');
    wiki_identifier = lambda raw_token: re.findall("[0-9]+", raw_token)[0];

    root = doc.getroot();
    root_mainNode = root.find(".//sentences");
    sentences = root.findall(".//sentence");
    newroot_mainNode = etree.Element("sentences");
    for sent_node in sentences:
	#print first_token(sent_node);
	if wiki_header( first_token(sent_node) ):
	    print first_token(sent_node);
	    print wiki_identifier( first_token(sent_node) );
	    #if len(newroot_mainNode) == 0:
		# starting;
		# ignore;
		#pass;
	    #else:
		#newdoc_mainNode = etree.Element("root");
		#docNode = etree.SubElement(newdoc_mainNode, "document");
		#newdoc_mainNode.append(newroot_mainNode);


	elif second_token == 'MySpecialNone' or wiki_header( second_token(sent_node) ):
	    print second_token(sent_node);
	    print wiki_identifier( second_token(sent_node) );

	    '''
	    outputFileName = os.path.join(outputDirectory, '%s.xml' %(sent_node.attrib['id']));
	    mod_doc = etree.ElementTree(root_mainNode);
	    mod_doc.write(outputFileName, encoding='utf-8', method='xml');
	    elem_attr = {};'''
	'''
	sent_node.attrib['id'] = repr( int(sent_node.attrib['id'])+int(elem_attr['id']) );
	sent_node.attrib['line'] = repr( int(sent_node.attrib['line'])+int(elem_attr['line']) );
	newroot_mainNode.append(sent_node);'''
    return;

def writeSegmentedWikiOutputIntoDocuments(xmlfiles, outputDirectory):
    elem_attr = {'id': '0', 'line': '0'};
    if os.path.isdir(outputDirectory) == False:
	os.system('mkdir -p %s' %(outputDirectory));

    for xmlfile in sortFileNamesByNumber(xmlfiles):
	print >>sys.stderr, xmlfile;
	doc = etree.parse(xmlfile);
	splitCoreNLPOutputForWiki(doc, outputDirectory, elem_attr);
    return;

def writeSegmentedCoreNLPOutputIntoDirectory(xmlfiles, outputDirectory):
    idx = 0;
    elem_attr = {'id': '0', 'line': '0'};
    if os.path.isdir(outputDirectory) == False:
	os.system('mkdir -p %s' %(outputDirectory));

    for xmlfile in sortFileNamesByNumber(xmlfiles):
	print >>sys.stderr, xmlfile;
	doc = etree.parse(xmlfile);
	splitCoreNLPOutputForSentences(doc, outputDirectory, elem_attr);
	del doc;
    return;

def runCoreNLPStanford(foldidx, folded_sentences):
    tmp_infile = '/tmp/%d.in' %(foldidx);
    tmp_outfile = os.path.split(tmp_infile+'.xml')[1];
    with codecs.open(tmp_infile, 'w') as outfile:
	for sent in folded_sentences:
	    print >>outfile, sent.strip();
    processing_cmd = 'sh stanford_corenlp-on_raw_data.sh %s' %(tmp_infile); 
    #processing_cmd = 'wc %s' %(tmp_infile);
    return (tmp_infile, tmp_outfile) if (subprocess.call(shlex.split(processing_cmd)) == 0) else None;

def runCoreNLPStanford_multi(args):
    return runCoreNLPStanford(*args);

def parallelRunCoreNLPStanford(filename, threadCount=0):
    if threadCount == 0:
	threadCount = multiprocessing.cpu_count();
    sentences, line_count = [], 0;
    with codecs.open(filename, 'r') as infile:
	for line in infile:
	    line_count += 1;
	    sentences.append(line.strip());
    folded_sentences = [];
    for foldrange in random_utils.epartition_indices(0, line_count):
	folded_sentences.append( sentences[foldrange[0]:foldrange[1]] );
    
    foldcount = len(folded_sentences);
    outputFiles = multiprocessing.Pool(threadCount).map(runCoreNLPStanford_multi, [(foldidx, folded_sentences[foldidx]) for foldidx in xrange(foldcount)], chunksize=int(log10(len(sentences))));
    return outputFiles;

def runCoreNLPLarge(filename, tmpdir='/tmp'):
    if os.path.isdir(tmpdir) == False:
	os.mkdir(tmpdir);
    for idx, segfiles in enumerate(parallelRunCoreNLPStanford(filename)):
	if segfiles == None:
	    print >>sys.stderr, "Fold %d failed to execute pipeline" %(idx);
	else:
	    os.system('cp %s %s %s' %(segfiles[0], segfiles[1], tmpdir));
    return;

def writeXMLFile(xsltFile, domObj):
    xslt = etree.parse(xsltFile);
    transform = lxml.etree.XSLT(xslt);
    newdom = transform(domObj);
    return etree.tostring(newdom, pretty_print=True);

def constparse_chunks(const_repr, terminalTokens):
    for term in terminalTokens:
	key = '%s)' %term;
	needle_idx = const_repr.find(key);
	if needle_idx != -1:
	    end_idx = needle_idx+len(key);
	    for ch in const_repr[end_idx:]:
		if ch == ')':
		    end_idx += 1;
		else:
		    break
	    yield const_repr[:end_idx].strip().replace(key, '*)').replace(' ', '_');
	    const_repr = const_repr[end_idx:].strip();
	else: 
	    print "could not find %s in %s" %(key, const_repr);

def convertSentenceToConLL(sent_xml_repr):
    import conll_utils;
    sent_node = etree.fromstring(sent_xml_repr);
    conll_sentence = [];
    terminalNodes = [];
    for token_node in sent_node.findall(".//token"):
	conll_line, isNer = {}, False;
	conll_line['id'] = token_node.attrib['id'];
	for child in token_node:
	    if child.tag == 'word': conll_line['form'] = child.text;
	    if child.tag == 'lemma': conll_line['lemma'] = child.text;
	    if child.tag == 'POS': conll_line['cpostag'] = child.text.strip();
	    if child.tag == 'NER' and child.text != 'O':
		conll_line.setdefault('feats', {})['nertype'] = child.text.strip();
		isNer = True;
	    if isNer == True and child.tag == 'NormalizedNER':
		conll_line.setdefault('feats', {})['normalized_ner'] = child.text.strip();
	    #if child.tag == 'TrueCaseText': conll_line['form'] = child.text.strip(); # Truecaser performance seems worse. 
	terminalNodes.append(conll_line['form']);
	conll_sentence.append(conll_line);
    const_parse = '';
    for parse_node in sent_node.findall("parse"):
	const_parse = parse_node.text.strip();
    if const_parse not in ['(())', '(ROOT ())', '(ROOT())']:
	for conll_line, chunk in zip(conll_sentence, constparse_chunks(const_parse, terminalNodes)):
	    conll_line['postag'] = chunk;
	    #print conll_line['form'], conll_line['postag'];
    try:
	assert( const_parse == ' '.join(conll_line['postag'].replace('_', ' ').replace('*', conll_line['form']) for conll_line in conll_sentence) );
    except AssertionError:
	print const_parse;
	print ' '.join(conll_line['postag'].replace('_', ' ').replace('*', conll_line['form']) for conll_line in conll_sentence);
	sys.exit(1);
    except KeyError:
	print const_parse;
	print ' '.join(conll_line.get('postag', 'NONE').replace('_', ' ').replace('*', conll_line['form']) for conll_line in conll_sentence);
	sys.exit(1);
    for depann_node in sent_node.findall(".//dependencies"):
	if depann_node.attrib['type'] == 'basic-dependencies':
	    # only convert basic dependencies in annotation
	    for dep_node in depann_node.findall(".//dep"):
		depLabel, head, token = '', -1, -1
		depLabel = dep_node.attrib['type']
		for child in dep_node:
		    if child.tag == 'governor': head = int(child.attrib['idx'])
		    if child.tag == 'dependent': token = int(child.attrib['idx'])
		conll_sentence[token-1]['head'] = str(head)
		conll_sentence[token-1]['deprel'] = depLabel
	else:
	    continue;
    # meta-information from stanford core nlp
    #metainfo = 'line:%s-sent:%s' %(sent_node.attrib['line'].strip(), sent_node.attrib['id'].strip());
    #return (metainfo, conll_sentence);
    return conll_sentence;

def convertStanfordCoreNLPXMLtoCoNLL(doc):
    root = doc.getroot();
    conll_sentences = [];
    for sent_node in root.findall(".//sentence"):
	conll_sentences.append( convertSentenceToConLL(etree.tostring(sent_node, encoding='utf-8', method='xml')) );
    return conll_sentences;

def convertSegmentedOutputtoCoNLL(inputdirectory, outputfile):
    import conll_utils;
    conll_sentences = [];
    with codecs.open(outputfile, 'w', 'utf-8') as outfile:
	for inputfile in sortFileNamesByNumber( os.listdir(inputdirectory) ):
	    inputfile = os.path.join(inputdirectory, inputfile);
	    print >>sys.stderr, inputfile;
	    try:
		doc = etree.parse(inputfile);
	    except:
		print inputfile;
		sys.exit(1);
	    conll_sentences.extend( convertStanfordCoreNLPXMLtoCoNLL(doc) );
	    if len(conll_sentences) > 50000:
		print >>sys.stderr, "Writing CoNLL sentences"
		conll_utils.sentences_to_conll07(outfile, conll_sentences);
		conll_sentences = [];
	if len(conll_sentences):
	    print >>sys.stderr, "Writing CoNLL sentences"
	    conll_utils.sentences_to_conll07(outfile, conll_sentences);
    return;

def convertOutputtoCoNLL(inputfile, outputfile):
    import conll_utils;
    conll_sentences = [];
    with codecs.open(outputfile, 'w', 'utf-8') as outfile:
	print >>sys.stderr, inputfile;
	doc = etree.parse(inputfile);
	conll_sentences.extend( convertStanfordCoreNLPXMLtoCoNLL(doc) );
	conll_utils.sentences_to_conll07(outfile, conll_sentences);
    return;

def readPtbParses(treebank):
    parses = [];
    with codecs.open(parsefile, 'r', 'utf-8') as infile:
	for line in infile:
	    yield line.strip();
	    #parses.append(line.strip());
    #return parses;

def convertDependencyToXML(dep_parse):
    if len(dep_parse) != len( filter(lambda entry: entry.get('head', '_') != '_', dep_parse) ):
	return None;
    main_node = etree.Element('dependencies');
    main_node.set('type', 'basic-dependencies');
    for dep_edge in dep_parse:
	dep_node = etree.Element('dep');
	dep_node.set('type', dep_edge['deprel']);
	governor_node = etree.SubElement(dep_node, 'governor');
	governor_node.set('idx', dep_edge['head']);
	governor_node.text = dep_parse[int(dep_edge['head'])-1]['form'] if dep_edge['head'] != '0' else 'ROOT';
	dependent_node = etree.SubElement(dep_node, 'dependent');
	dependent_node.set('idx', dep_edge['id']);
	dependent_node.text = dep_edge['form'];
	main_node.append(dep_node);
    return main_node;

def updateSyntacticInformation(doc, parses, dep_parses):
    root = doc.getroot();
    root_mainNode = root if root.tag == "sentences" else root.find(".//sentences");
    sentences = root.findall(".//sentence");
    # remove all sentences from the xml content
    for sent_node in sentences: 
	root_mainNode.remove(sent_node);
    idx = 0;
    for sent_node in sentences:
	if parses[idx] == None or dep_parses[idx] == None:
	    root_mainNode.append(sent_node);
	    continue;
	parse_node = sent_node.find(".//parse");
	if parse_node != None:
	    sent_node.remove(parse_node);
	parse_node = etree.SubElement(sent_node, "parse");
	parse_node.text = parses[idx].strip();
	for dep_node in sent_node.findall(".//dependencies"):
	    sent_node.remove(dep_node);
	dep_node = convertDependencyToXML(dep_parses[idx])
	if dep_node != None:
	    sent_node.append(dep_node);
	root_mainNode.append(sent_node);
	idx += 1;
    return root;

# http://snipplr.com/view/25657/indent-xml-using-elementtree/
def indentXMLNodes(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
	if not elem.text or not elem.text.strip():
	    elem.text = i + "  "
	if not elem.tail or not elem.tail.strip():
	    elem.tail = i
	for elem in elem:
	    indentXMLNodes(elem, level+1)
	if not elem.tail or not elem.tail.strip():
	    elem.tail = i
    else:
	if level and (not elem.tail or not elem.tail.strip()):
	    elem.tail = i
    
def addParsestoXMLFromOtherSources(xmlfile, parsesfile, depfile):
    import conll_utils;
    parser = etree.XMLParser(remove_blank_text=True);
    doc = etree.parse(xmlfile, parser);
    const_parses = [line for line in codecs.open(parsesfile, 'r', 'utf-8')];
    dep_parses = [parse for parse in conll_utils.sentences_from_conll(codecs.open(depfile, 'r', 'utf-8'))];
    mod_root = updateSyntacticInformation(doc, const_parses, dep_parses);
    # NECESSARY BECAUSE LXML does not allow pretty printing for nodes with text data. 
    # EXACT INFORMATION CAN BE FOUND AT
    # http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
    indentXMLNodes(mod_root);
    print etree.tostring(mod_root, encoding='utf-8', method='xml');

def addParsestoSegmentedXMLFromOtherSources(xmlinputdirectory, parsesfile, depfile, xmloutputdirectory):
    import conll_utils;
    const_parses = codecs.open(parsesfile, 'r', 'utf-8');
    dep_parses = conll_utils.sentences_from_conll(codecs.open(depfile, 'r', 'utf-8'));
    for xmlfile in sortFileNamesByNumber( os.listdir(xmlinputdirectory) ):
	xmlfilepath = os.path.join(xmlinputdirectory, xmlfile);
	print >>sys.stderr, xmlfilepath
	outxmlfilepath = os.path.join(xmloutputdirectory, xmlfile);
	parser = etree.XMLParser(remove_blank_text=True);
	doc = etree.parse(xmlfilepath, parser);
	mod_root = updateSyntacticInformation(doc, [const_parses.next()], [dep_parses.next()]);
	# NECESSARY BECAUSE LXML does not allow pretty printing for nodes with text data. 
	# EXACT INFORMATION CAN BE FOUND AT
	# http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
	indentXMLNodes(mod_root);
	mod_doc = etree.ElementTree(mod_root);
	mod_doc.write(outxmlfilepath, encoding='utf-8', method='xml');
	'''
	with codecs.open(outxmlfilepath, 'w', 'utf-8') as outfile:
	    try:
		print >>outfile, etree.tostring(mod_root, encoding='utf-8', method='xml');
	    except UnicodeDecodeError:
		print >>sys.stderr, xmlfilepath.upper()
		sys.exit(1);'''
    return;

def moses_normalizedToken(token):
    token = token.replace('&', '&amp;');
    token = token.replace('|', '_PIPE_');
    token = token.replace('<', '&lt;');
    token = token.replace('>', '&gt;');
    token = token.replace("'", '&apos;');
    token = token.replace('"', '&quot;');
    return token;

def getTokens(conll_sentence):
    tokens = [];
    for tok in conll_sentence:
	fields = [];
	fields.append( moses_normalizedToken(tok['form']) );
	fields.append( moses_normalizedToken(tok['lemma']) );
	if tok['cpostag'] == '_':
	    fields.append( 'X' );
	else:
	    fields.append( tok['cpostag'] );
	if tok['head'] != '_' and tok['head'] != 0:
	    fields.append( conll_sentence[int(tok['head'])-1]['cpostag'] );
	    fields.append( '%s_%s' %(moses_normalizedToken(tok['lemma']), conll_sentence[int(tok['head'])-1]['cpostag'] ) );
	    if tok['deprel'] != '':
		fields.append( '%s_%s' %(tok['deprel'], conll_sentence[int(tok['head'])-1]['cpostag'] ) );
	elif tok['head'] == 0:
	    fields.append( 'ROOT' );
	    fields.append( '%s_ROOT' %(moses_normalizedToken(tok['lemma'])) );
	    if tok['deprel'] != '':
		fields.append( '%s_ROOT' %(tok['deprel'], conll_sentence[int(tok['head'])-1]['cpostag'] ) );
	else:
	    fields.append( 'X' );
	    fields.append('%s_X' %(moses_normalizedToken(tok['lemma'])) );
	    fields.append('X_X' );
	handleSpaces = lambda s: s.replace(u'\xa0', u'+');
	if fields[0].startswith('0870'):
	    print repr(fields[0])
	tokens.append( '|'.join(map(handleSpaces, fields)) );
    '''return ['%s|%s' %(field1,field2) for field1,field2 in zip( \
	    map(moses_normalizedToken, [line['form'] for line in conll_sentence]), \
	    map(moses_normalizedToken, [line['lemma'] for line in conll_sentence]) \
	    )];'''
    return tokens;	

def convertCoNLLToMosesTokenized(conllfile, outputfile, blanksentids=None):
    blank_sent_ids = [];
    if blanksentids != None:
	blank_sent_ids = [int(sentid) for sentid in open(blanksentids)];
    #print blanksentids, blank_sent_ids;
    with codecs.open(outputfile, 'w', 'utf-8') as outfile:
	tokenizedSentences = [];
	sentCount = 0;
	with codecs.open(conllfile, 'r', 'utf-8') as infile:
	    for sentence in conll_utils.sentences_from_conll(infile):
		sentCount += 1;
		while sentCount in blank_sent_ids:
		    tokenizedSentences.append( [] );
		    sentCount += 1;
		tokenizedSentences.append( getTokens(sentence) );
		if not sentCount%100000:
		    for sent in tokenizedSentences:
			print >>outfile, ' '.join(sent);
		    tokenizedSentences = [];
	    if len(tokenizedSentences):
		for sent in tokenizedSentences:
		    print >>outfile, ' '.join(sent);
    return;

if __name__ == '__main__':
    #runCoreNLPLarge(sys.argv[1], sys.argv[2]);
    #writeSegmentedCoreNLPOutputIntoDirectory(sys.argv[2:], sys.argv[1]);
    #writeSegmentedWikiOutputIntoDocuments(sys.argv[2:], sys.argv[1]);
    convertSegmentedOutputtoCoNLL(sys.argv[1], sys.argv[2]) if os.path.isdir(sys.argv[1]) else True;
    #convertOutputtoCoNLL(sys.argv[1], sys.argv[2]) if os.path.isfile(sys.argv[1]) else True;
    #addParsestoXMLFromOtherSources(sys.argv[1], sys.argv[2], sys.argv[3]);
    #addParsestoSegmentedXMLFromOtherSources(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);
    #convertCoNLLToMosesTokenized(sys.argv[1], sys.argv[2])#, sys.argv[3]);
