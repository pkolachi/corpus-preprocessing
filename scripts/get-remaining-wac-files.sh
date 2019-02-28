#!/bin/bash

CURDIR="$HOME/Documents/chalmers-work/corpus-preprocessing";
partition_name=$1;
du -s "$CURDIR/corpora-resources/wac/ukWac/split/$partition_name/*" | sort -nk1 | cut -f2 | egrep -v "`ls $CURDIR/corpora-resources/wac/ukWac/stanford-corenlp-xml/$partition_name | sed 's/\.xml//'`"
