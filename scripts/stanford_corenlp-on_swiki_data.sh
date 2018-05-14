#!/bin/bash

export JRE_HOME="$HOME/Documents/softwares/java/jre1.8.0_111.jre/Contents/Home"  # -- gfold server
export JRE_HOME="/usr"  # -- laptop
export JRE_HOME="$HOME/Documents/softwares/java/jre1.8.0_40"  # -- ttitania server

export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2018-02-27"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2016-10-31"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2015-12-09"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2015-04-20"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-10-31"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-08-27"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-01-04"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2013-11-12"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
JAVA="$JRE_HOME/bin/java"

"$JAVA" -Xmx8G -cp "$STANFORD_CORENLP_DIR/*" edu.stanford.nlp.pipeline.StanfordCoreNLP  \
    -annotators tokenize,ssplit,pos,lemma,ner,parse  \
    -tokenize.options "americanize=false" \
    -clean.allowflawedxml "true" \
    -clean.xmltags ".*" \
    -clean.sentenceendingtags "br" \
    -threads 8 \
    -filelist $1 \
    -outputDirectory $2
