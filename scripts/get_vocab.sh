#!/bin/bash

TAB=`echo -e "\t"`
PARALLEL="--parallel=8"

mkdir -p "$PWD/tmp";
bzcat $1 | grep -v "^$" | \
    cut -f2,4 | LC_ALL="C" tr '[:upper:]' '[:lower:]' | \
    LC_ALL="C" sort -k1"$PARALLEL" -T "$PWD/tmp" | uniq -c | \
    sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
    sort -S8G -k1,1nr"$PARALLEL" --stable -t"$TAB" -T "$PWD/tmp" > "$2.vcb"

cat "$2.vcb" | \
    LC_ALL="C" sort -S8G -k2,3"$PARALLEL" --stable -t"$TAB" -T"$PWD/tmp" | \
    awk -F'\t' '
{ 
    if(key!=""$2) {
	print count"\t"key"\t"value; count=$1; key=""$2; value=""$3;
    } else {
	value=value":::"$3; count+=$1;
    } 
}' | \
    sort -S8G -k1,1nr"$PARALLEL" --stable -t"$TAB" -T "$PWD/tmp" > $2.lexicon


