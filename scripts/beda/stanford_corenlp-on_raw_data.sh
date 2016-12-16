
export STANFORD_CORENLP_DIR="$HOME/Documents/softwares/nlp-tools/language-specific/english/stanford-tools/stanford-corenlp-full-2013-11-12"

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

java -Xmx20g -cp "$STANFORD_CORENLP_DIR/*" edu.stanford.nlp.pipeline.StanfordCoreNLP \
-props $SCRIPTPATH/stanford_corenlp-mtprops.txt \
-encoding ISO-8859-1 \
-filelist $1 \
-outputDirectory Documents/chalmers-work/corpus-preprocessing/corpora-resources/monolingual/english/europarl/europarl-v7.stanfordcore_en/seg_output 
