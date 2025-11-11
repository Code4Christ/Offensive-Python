#!/bin/bash

url="http://83.136.254.84:39688"

for i in {1..10}; do
    for link in $(curl -s -X POST "$url/documents.php" | grep -oP "\/documents.*?.pdf"); do
        echo "Downloading: $link"
        wget -q --content-disposition -c "${url}/${link}"
    done
done


