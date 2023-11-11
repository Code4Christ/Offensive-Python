# Import necessary modules
import socket
import threading
from IPy import IP

# Function to initiate the scan on the target
def scan(target):
    converted_ip = check_ip(target)  # Convert target to IP address if needed
    print(f'\n [-_0 Scanning Target] {str(target)}')

    # Loop through ports and create threads to scan each port concurrently
    for port in range(1, 100000):
        thread = threading.Thread(target=scan_port, args=[converted_ip, port])
        thread.start()
        # Alternative: scan_port(converted_ip, port)

# Function to check if the input is an IP address or domain and convert it to IP if necessary
def check_ip(ip):
    try:
        IP(ip)
        return ip
    except ValueError:
        return socket.gethostbyname(ip)

# Function to retrieve banner information from a socket
def get_banner(sock):
    return sock.recv(1024)

# Function to scan a specific port on a target IP address
def scan_port(ipaddress, port):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        sock.connect((ipaddress, port))

        try:
            banner = get_banner(sock)  # Attempt to grab the banner from the connected port
            print(f'[+] Open Port {port} : ' + str(banner.decode().strip("\n")))
        except:
            print(f'[+] Open Port {port}')

    except:
        # Connection to the port failed (likely closed)
        # print(f'[-] Port {port} is closed')
        pass

# Main execution block
if __name__ == "__main__":
    targets = input("[+] Enter Target(s) to Scan (split multiple targets with ,): ")

    if "," in targets:
        # If there are multiple targets, split them and scan each one
        for ip_add in targets.split(","):
            print(ip_add.strip(','))
            scan(ip_add.strip(','))
    else:
        # If only one target, scan it directly
        scan(targets)
