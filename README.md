# Passive Subdomain Finder (OSINT)

A lightweight reconnaissance tool written in Python that enumerates subdomains using public Certificate Transparency (CT) logs via crt.sh without sending aggressive traffic to the target infrastructure.

## Key Features
- **Passive Enumeration:** Gathers domain intelligence safely through publicly logged SSL/TLS certificates.
- **DNS Resolution Verification:** Performs lightweight DNS checks to identify which discovered subdomains currently point to active IP addresses.
- **Duplicate & Wildcard Sanitization:** Cleans wildcard entries (`*.`) and filters duplicate entries automatically.

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/passive-subdomain-finder.git
   cd passive-subdomain-finder