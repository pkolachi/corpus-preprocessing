PARSER_DIR="$HOME/Documents/chalmers-work/courses/2014_tda231/project/resources/multiviewparser.v2"
#PARSER_DIR="."

#WS="../../sve48/workspace"
#CP="$WS/depsrl/bin:$WS/nlputils/bin:$WS/nlputils/external/trove.jar:$WS/nlputils/external/bzip2.jar"
CP="$PARSER_DIR/depparser.jar:$PARSER_DIR/external/trove.jar:$PARSER_DIR/external/bzip2.jar"
MEM=8000M
JAVA="java"
#JAVA="$HOME/Documents/softwares/java/jre1.8.0_40/bin/java"

CLUSTER_EXPERIMENT=true

FILE=sv-ud-train.conll.v2
FILE2=en-ud-train.conll.v2
TESTFILE=sv-ud-dev-blind.conll.v2
TESTFILE2=en-ud-dev-blind.conll.v2
GOLDTESTFILE=sv-ud-dev.conll.v2
GOLDTESTFILE2=en-ud-dev.conll.v2

ENC_FILE=mixed_o1.enc.v2
FILTER_MODEL=sv-ud_filter_o1.model.v2
FILTER_MODEL2=en-ud_filter_o1.model.v2

PARSER_MODEL=sv+en-ud_1storder_nonproj.model.v2
LOG=$PARSER_MODEL.log
rm -f $LOG

UNLABELED=false

# 1st- or 2nd-order search
SEARCH=1
# number of trees to use from each treebank (-1 = all)
SUBSET=-1
SUBSET2=-1

MAKE_ENCS_AND_FILTERS=true

# 1. MAKE ENCODING

if [ x$MAKE_ENCS_AND_FILTERS = xtrue ]; then
time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -makeEncoders \
 -inFile=$FILE \
 -inFile2=$FILE2 \
 -encoderFile=$ENC_FILE \
 -nonproj="PROJECTIVIZE" \
 -unlabeled=$UNLABELED > $LOG 2>&1

USED_FILTERS="[LENGTH]"
ALG_NAMES="[NONE]"
ALG_ARGS="[NONE]"
WS="[ [ ] ]"

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -trainFilter \
 -inFile=$FILE \
 -filterFile=$FILTER_MODEL \
 -filterPOS=true \
 -encoderFile=$ENC_FILE \
 -unlabeled=$UNLABELED \
 -useCoarse=true \
 -useFine=false \
 -useLemma=false \
 -clusterExperiment=$CLUSTER_EXPERIMENT \
 -usedFilters="$USED_FILTERS" \
 -nonproj="PROJECTIVIZE" \
 -fAlgNames="$ALG_NAMES" \
 -fAlgArgs="$ALG_ARGS" \
 -filterWeights="$WS" >> $LOG 2>&1 

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -trainFilter \
 -inFile=$FILE2 \
 -filterFile=$FILTER_MODEL2 \
 -filterPOS=true \
 -encoderFile=$ENC_FILE \
 -unlabeled=$UNLABELED \
 -useCoarse=true \
 -useFine=false \
 -useLemma=false \
 -clusterExperiment=$CLUSTER_EXPERIMENT \
 -usedFilters="$USED_FILTERS" \
 -nonproj="PROJECTIVIZE" \
 -fAlgNames="$ALG_NAMES" \
 -fAlgArgs="$ALG_ARGS" \
 -filterWeights="$WS" >> $LOG 2>&1 

fi

SECPARSES=NONE
APPROXN=64 
SINGLE_ROOT=true
SIMPLIFIED_SHARED=false

# learning paramaters

# max 80 000 000
ALG_NAME=OnlineAlgorithm
SIZE=20000000
C=0.01
NROUNDS=12
MAXLOSS=true
SQRT=true
ALG_ARGS="nRounds=$NROUNDS printDots=10 useNewLinear=true modelSize=$SIZE PAUpdate C=$C maximizeLoss=$MAXLOSS sorted=true sqrt=$SQRT"

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -train \
 -inFile=$FILE \
 -inFile2=$FILE2 \
 -subsetSize=$SUBSET \
 -subsetSize2=$SUBSET2 \
 -secParseFileName=$SECPARSES \
 -searchMode=$SEARCH \
 -singleRoot=$SINGLE_ROOT \
 -modelFile=$PARSER_MODEL \
 -unlabeled=$UNLABELED \
 -filterFile=$FILTER_MODEL \
 -filterFile2=$FILTER_MODEL2 \
 -encoderFile=$ENC_FILE \
 -simplifiedShared=$SIMPLIFIED_SHARED \
 -clusterExperiment=$CLUSTER_EXPERIMENT \
 -useCoarse=true \
 -useFine=false \
 -useLemma=false \
 -nonproj="PROJECTIVIZE" \
 -algName=$ALG_NAME \
 -algArgs="$ALG_ARGS" >> $LOG 2>&1

SECOND_VIEW=false

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -run \
 -modelFile=$PARSER_MODEL \
 -inFile=$TESTFILE \
 -outFileName="$TESTFILE-1storder_nonproj.out" \
 -deproj=true \
 -isType2=$SECOND_VIEW

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -run \
 -modelFile=$PARSER_MODEL \
 -inFile=$GOLDTESTFILE \
 -outFileName="$GOLDTESTFILE-1storder_nonproj.out" \
 -deproj=true \
 -isType2=$SECOND_VIEW

SECOND_VIEW=true

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -run \
 -modelFile=$PARSER_MODEL \
 -inFile=$TESTFILE2 \
 -outFileName="$TESTFILE2-1storder_nonproj.out" \
 -deproj=true \
 -isType2=$SECOND_VIEW

time $JAVA -Xmx$MEM -cp $CP \
 it.unitn.disi.depsrl.parser.DependencyParser -run \
 -modelFile=$PARSER_MODEL \
 -inFile=$GOLDTESTFILE2 \
 -outFileName="$GOLDTESTFILE2-1storder_nonproj.out" \
 -deproj=true \
 -isType2=$SECOND_VIEW
