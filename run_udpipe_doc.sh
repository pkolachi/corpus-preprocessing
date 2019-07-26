#!/bin/bash

UDDIR="$HOME/Documents/softwares/nlp-tools/pipelines/udpipe/udpipe-1.2.0-bin/bin-linux64";
#UDDIR="$HOME/Documents/softwares/nlp-tools/pipelines/udpipe/udpipe-1.1.0-bin/bin-linux64";

"${UDDIR}/udpipe" \
    --output=conllu \
    --outfile="{}.conllu"\
    --tokenize --tag --parse \
    $1 ${@:2}

# --input=conllu \
