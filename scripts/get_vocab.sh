#!/bin/bash

TAB=`echo -e "\t"`
#SORT_OPTS="-S 50% --parallel=8 -T $PWD/tmp";
SORT_OPTS="-S 50% -T $PWD/tmp"

mkdir -p "$PWD/tmp";
bzcat $1 | grep -v "^#" | grep -v "^$" | \
    cut -f2,4 | LC_ALL="C" tr '[:upper:]' '[:lower:]' | \
    LC_ALL="C" sort $SORT_OPTS -k1 | uniq -c | \
    sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.vcb"

bzcat $1 | grep -v "^#" | grep -v "^$" | \
    cut -f2,3,4,6 | \
    LC_ALL="C" sort $SORT_OPTS | uniq -c | \
    sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
    LC_ALL="C" sort $SORT_OPTS -k4,4 -k3,3 -k2,2 | \
    awk '{print $1"\t"$4"\t"$3"\t"$2"\t"$5;}' > "$2.morph_lexicon"

cat "$2.vcb" | \
    LC_ALL="C" sort $SORT_OPTS -k2,3 --stable -t"$TAB" | \
    awk -F'\t' '
{ 
    if(key!=""$2) {
	print count"\t"key"\t"value; count=$1; key=""$2; value=""$3;
    } else {
	value=value":::"$3; count+=$1;
    } 
}' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.lexicon"


