#!/bin/bash

sed -e 's/``/"/g' -e 's/'\'\''/"/g' -e 's/-LRB-/(/g' -e 's/-RRB-/)/g' -e 's/-LSB-/[/g' -e 's/-RSB-/]/g' -e 's/-LCB-/{/g' -e 's/-RCB-/}/g'
