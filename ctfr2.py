#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
    CTFR - 04.03.18.02.10.00 - Sheila A. Berta (UnaPibaGeek)
    Modified by ChatGPT to support -f flag and retry logic
------------------------------------------------------------------------------
"""

import re
import time
import requests

version = 1.2

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--domain', type=str, help="Target domain.")
    group.add_argument('-f', '--file', type=str, help="Path to file with domains (one per line).")
    parser.add_argument('-o', '--output', type=str, help="Output file.")
    return parser.parse_args()

def banner():
    global version
    b = '''
          ____ _____ _____ ____  
         / ___|_   _|  ___|  _ \\ 
        | |     | | | |_  | |_) |
        | |___  | | |  _| |  _ < 
         \\____| |_| |_|   |_| \\_\\
    
     Version {v} - Hey don't miss AXFR!
    Made by Sheila A. Berta (UnaPibaGeek)
    '''.format(v=version)
    print(b)

def clear_url(target):
    return re.sub('.*www\\.', '', target, 1).split('/')[0].strip()

def save_subdomains(subdomain, output_file):
    with open(output_file, "a") as f:
        f.write(subdomain + '\n')

def search_subdomains(domain, tlds):
    subdomains = set()
    for tld in tlds:
        target = f"{domain}.{tld}"
        print(f"[+] Searching for subdomains of {target}...")

        req = None
        for attempt in range(1, 6):
            try:
                req = requests.get(f"https://crt.sh/?q=%.{target}&output=json", timeout=10)
                req.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"[X] Attempt {attempt}/5 failed for {target}: {e}")
                if attempt < 5:
                    time.sleep(2)
                else:
                    print(f"[!] Giving up on {target} after 5 attempts.")
                    req = None

        if not req or req.status_code != 200:
            continue

        try:
            json_data = req.json()
            if not json_data:
                print(f"[X] No subdomains found for {target}.")
                continue

            for value in json_data:
                subdomain = value.get('name_value', '').strip()
                if '*' in subdomain:
                    continue
                subdomains.add(subdomain)

        except ValueError:
            print(f"[X] Error parsing JSON response for {target}!")

    return list(subdomains)

def main():
    banner()
    args = parse_args()

    output = args.output
    domains = []

    if args.domain:
        domains = [clear_url(args.domain)]
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                domains = [clear_url(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[X] File not found: {args.file}")
            return

    tlds = [
        'com', 'org', 'net', 'ua', 'com.ua', 'tech', 'dev', 'finance', 'shop', 'io',
        'app', 'ai', 'biz', 'click', 'eu', 'store', 'online', 'co', 'b2b'
    ]

    for domain in domains:
        print(f"\n[!] ---- TARGET: {domain} ---- [!]")
        subdomains = search_subdomains(domain, tlds)
        subdomains = sorted(set(subdomains))

        for subdomain in subdomains:
            print(f"[-]  {subdomain}")
            if output:
                save_subdomains(subdomain, output)

    print("\n[!] Done. Have a nice day! ;)")

if __name__ == '__main__':
    main()
