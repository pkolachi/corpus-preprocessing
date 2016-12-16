export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2013-11-12"
#export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2014-10-31"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

java -Xmx4g -cp "$STANFORD_CORENLP_DIR/*" edu.stanford.nlp.pipeline.StanfordCoreNLP \
-props stanford_corenlp-mtprops.txt \
-threads 3 \
-file $1 
