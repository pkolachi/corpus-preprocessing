
import itertools, os, sys;

srcDirectory, tgtDirectory = sys.argv[1], sys.argv[2];
srcDirectory, tgtDirectory = os.path.normpath(srcDirectory), os.path.normpath(tgtDirectory);

for dirpath, dirList, fileList in os.walk(srcDirectory):
    tgtdirpath = dirpath.replace(srcDirectory, tgtDirectory);
    
    tgtdirList = itertools.imap(os.path.join, itertools.repeat(tgtdirpath, len(dirList)), (dirname.replace(srcDirectory, tgtDirectory) for dirname in dirList));
    for tgtdir in tgtdirList:
	if os.path.isdir(tgtdir) == False:
	    print "%s: Target directory does not match" %(tgtdir);
    
    tgtfileList = itertools.imap(os.path.join, itertools.repeat(tgtdirpath, len(fileList)), (filename.replace(srcDirectory, tgtDirectory) for filename in fileList));
    srcfileList = itertools.imap(os.path.join, itertools.repeat(dirpath, len(fileList)), fileList);
    for srcfile, tgtfile in itertools.izip(srcfileList, tgtfileList):
	if os.path.isfile(tgtfile) == False or os.system('cmp "%s" "%s" > /dev/null 2> /dev/null' %(srcfile, tgtfile)) != 0:
	    print "%s: Target file does not match" %(tgtfile);
