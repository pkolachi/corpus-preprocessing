export MATETOOLS_JAR="$HOME/Documents/softwares/nlp-tools/parsers/mate-tools/anna-3.61.jar"

java -Xmx16G -classpath "$MATETOOLS_JAR" is2.parser.Parser \
    -model $2 \
    -train $1 \
    -i 10 -hsize 500000001 -cores 8 \
    -decodeTH 0.3

