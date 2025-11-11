""" 
---------------------------
BYPASS BASIC AUTHENTICATION
---------------------------

1. Try to use what you learned in this section to access the 'reset.php' page and delete all files. Once all files are deleted, you should get the flag.
"""

# Import Request to send web request to the internet
import requests
import sys
import requests
import subprocess
# Module to display output in different colors.
from colorama import Fore, Back, Style
"""
Disable the display of certificate warnings when requests 
are made to websites using insecure certificates. This can 
be useful in scenarios where targeted web applications use 
self-signed certificates as is the case in the AWAE labs.
"""
requests.packages.urllib3.\
disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def main():
    """
    Main entry point:
    - validate CLI args
    - build request info
    - simulate (or actually perform) the request
    - format and print the response blocks
    """
    # If the script is ran without specify the target
    if len(sys.argv) != 2:
        print(f"In CLI, Usage should be: {sys.argv[0]} target")
        print(f"Example: {sys.argv[0]} 10.0.0.1")
        print(f"Example: {sys.argv[0]} manageengine")
        sys.exit(1)

    # Obtain taregt from CLI
    target = sys.argv[1].strip().rstrip('/')   # from CLI202

    DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "",  # can set if needed
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    }

    # Optional headers to mimic your Burp capture
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://{target}",
        "Referer": "http://{target}/",
        # don't set Content-Type here — requests will set the correct multipart boundary
    }
    
    # ============================ UPLOAD URL of TARGET ============================ #
    upload_url = f"http://{target}/"

    # ============================ Initiate the Request to UPLOAD PHP FILE  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(upload_url, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    

    # ============================ FORMAT OUTPUT ============================ #
    print("\n======= Johnny Custom Exploit Development =======\n")
    print(format_text("REQUEST METHOD:", r.request.method))
    print(format_text("REQUEST URL:", r.request.url))
    print(format_text("REQUEST HEADERS | r.headers is: :", r.request.headers))
    print(format_text("REQUEST BODY (raw):", r.request.body))   # shows form-encoded body
    print(format_text("RESPONSE STATUS | r.status_code is:", r.status_code))
    print(format_text("RESPONSE COOKIES | r.cookies is:", r.cookies))
    print(format_text("RESPONSE CONTENT-LENGTH:", len(r.text)))
    print(format_text("RESPONSE (first 300 chars):\n", r.text))

def format_text(title,item):
  """
    Helper to create a nicely formatted console output block.

    - title: short label for the section (e.g. "r.status_code is:")
    - item: item to display (will be stringified)
    Returns a string that contains the title, a separator, the item, and a short marker.
  """
  cr = '\r\n'
  section_break = cr +  "*" * 20 + cr
  item = str(item)
  text = Style.BRIGHT + Fore.RED + title + Fore.RESET + section_break + item + section_break + '\t'
  return text

if __name__ == "__main__":
    main()