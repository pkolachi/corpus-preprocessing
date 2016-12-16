export JRE_HOME="$HOME/Documents/softwares/java/jre1.8.0_40/"
export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-10-31"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

java -Xmx12G -cp "$STANFORD_CORENLP_DIR/*" edu.stanford.nlp.pipeline.StanfordCoreNLP  \
-annotators tokenize,ssplit,pos,lemma,ner,parse  \
-threads 1 \
-filelist $1 \
-outputDirectory $2
