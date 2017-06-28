#!/bin/bash

TAB=`echo -e "\t"`
#SORT_OPTS="-S 50% --parallel=8 -T $PWD/tmp";
SORT_OPTS="-S 50% -T $PWD/tmp"
export LC_ALL=C

MORPH_TAGGED=true

mkdir -p "$PWD/tmp";

transformer1="tr '[:upper:]' '[:lower:]'"
transformer2="awk '{print tolower($0)}'"


# lower-cased surface forms
bzcat $1 | grep -v -e "^#" -e "^$" | head -n 10000 | \
    cut -f2,4 | awk '{print tolower($1)"\t"$2;}' | \
    sort $SORT_OPTS -k1 | uniq -c | \
    sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.vcb"

cat "$2.vcb" | head -n 10000 | \
    sort $SORT_OPTS -k2,3 --stable -t"$TAB" | \
    awk -F'\t' '
{ 
    if(key!=""$2) {
	print count"\t"key"\t"value; count=$1; key=""$2; value=""$3;
    } else {
	value=value":::"$3; count+=$1;
    } 
}' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.taglex"

if $MORPH_TAGGED ; then
    bzcat $1 | grep -v -e "^#" -e "^$" | head -n 10000 | \
	cut -f3,4 | \
	sort $SORT_OPTS -k1 | uniq -c | \
	sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
	sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.lemmas"
    
    bzcat $1 | grep -v -e "^#" -e "^$" | head -n 10000 | \
	cut -f2,3,4,6 | awk '{print tolower($1)"\t"$2"\t"$3"\t"$4;}' | \
	sort $SORT_OPTS -k1 | uniq -c | \
	sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
	sort $SORT_OPTS -k4,4 -k3,3 -k2,2 | \
	awk '{print $1"\t"$4"\t"$3"\t"$2"\t"$5;}' > "$2.morphlex"
fi



