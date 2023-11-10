import socket
import threading
from IPy import IP


def scan(target):
    converted_ip = check_ip(target)
    print(f'\n [-_0 Scanning Target] {str(target)}')
    for port in range(1, 100000):
        thread = threading.Thread(target=scan_port, args=[converted_ip, port])
        thread.start()
        # scan_port(converted_ip, port)


def check_ip(ip):
    try:
        IP(ip)
        return (ip)
    except ValueError:
        return socket.gethostbyname(ip)


def get_banner(sock):
    return sock.recv(1024)


def scan_port(ipaddress, port):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        sock.connect((ipaddress, port))
        try:
            banner = get_banner(sock)  # grab the banner from the website
            print(f'[+] Open Port {port} : ' + str(banner.decode().strip("\n")))
        except:
            print(f'[+] Open Port {port}')

    except:
        #print(f'[-] Port {port} is closed')
        pass


if __name__ == "__main__":
    targets = input("[+] Enter Target(s) to Scan (split multiple targets with ,): ")

    if "," in targets:
        for ip_add in targets.split(","):
            print(ip_add.strip(','))
            scan(ip_add.strip(','))
    else:
        scan(targets)
