#!/bin/bash

if [ $# -eq 0 ]
then
    echo "score.sh reffile testfile [-c]"
    exit
fi

ref=$1;
tst=$2;
langs="src";
langt="tgt";
capitalization="$3";

curpath=`dirname $0`
moses_generic="/Users/prakol/Documents/softwares/nlp-tools/mt-systems/moses/mosesdecoder/scripts/generic"

$curpath/convert2sgm $tst tst $langs $langt > /tmp/tst.$$.sgm
$curpath/convert2sgm $ref ref $langs $langt > /tmp/ref.$$.sgm
$curpath/convert2sgm $tst src $langs $langt > /tmp/src.$$.sgm

$moses_generic/mteval-v12.pl \
    -r /tmp/ref.$$.sgm \
    -s /tmp/src.$$.sgm \
    -t /tmp/tst.$$.sgm ${capitalization}

rm /tmp/ref.$$.sgm /tmp/src.$$.sgm /tmp/tst.$$.sgm
