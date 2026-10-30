import sys
import socket
import requests
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SubdomainFinder/1.0"
}

def clean_domain(domain: str) -> str:
    """ตัดแต่งชื่อโดเมนให้เหลือเฉพาะ FQDN"""
    domain = domain.strip().lower()
    if "://" in domain:
        domain = urlparse(domain).netloc
    return domain.split(":")[0]

def resolve_dns(subdomain: str) -> str:
    """ตรวจสอบว่า Subdomain มีการชี้ DNS ไปยัง IP ใด"""
    try:
        ip = socket.gethostbyname(subdomain)
        return ip
    except (socket.gaierror, socket.timeout):
        return "Unresolved"

def fetch_subdomains(target_domain: str):
    target_domain = clean_domain(target_domain)
    print(f"\n{Fore.CYAN}=== Passive Subdomain Discovery: {Style.BRIGHT}{target_domain}{Style.RESET_ALL} ===\n")
    print(f"[*] Querying Certificate Transparency (crt.sh)...")

    url = f"https://crt.sh/?q=%25.{target_domain}&output=json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=25)
        if response.status_code != 200:
            print(f"{Fore.RED}[!] Failed to fetch records (HTTP {response.status_code}).")
            sys.exit(1)
        
        entries = response.json()
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}[!] Request timed out. crt.sh may be under heavy load.")
        sys.exit(1)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"{Fore.RED}[!] Error querying service: {e}")
        sys.exit(1)

    raw_subdomains = set()
    for item in entries:
        names = item.get("name_value", "").split("\n")
        for name in names:
            name = name.strip().lower()
            if name.startswith("*."):
                name = name[2:]
            if name.endswith(target_domain) and name != target_domain:
                raw_subdomains.add(name)

    if not raw_subdomains:
        print(f"{Fore.YELLOW}[-] No subdomains discovered for this domain.")
        return

    print(f"{Fore.GREEN}[+] Found {len(raw_subdomains)} unique subdomain(s). Resolving DNS status...{Style.RESET_ALL}\n")
    print(f"{'Subdomain':<40} | {'Status':<12} | {'Resolved IP'}")
    print("-" * 75)

    active_count = 0
    for sub in sorted(raw_subdomains):
        ip = resolve_dns(sub)
        if ip != "Unresolved":
            active_count += 1
            print(f"{Fore.GREEN}{sub:<40}{Style.RESET_ALL} | {Fore.GREEN}ACTIVE{Style.RESET_ALL}      | {ip}")
        else:
            print(f"{Fore.LIGHTBLACK_EX}{sub:<40} | INACTIVE    | -{Style.RESET_ALL}")

    print("-" * 75)
    print(f"Summary: {Fore.GREEN}{active_count} Active{Style.RESET_ALL}, {len(raw_subdomains) - active_count} Inactive\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python subfinder.py <target-domain>")
        sys.exit(1)

    fetch_subdomains(sys.argv[1])