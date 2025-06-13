#!/usr/bin/env python3
"""
Script to download all Scripts and Policies from a Jamf Pro server using Bearer token auth,
save them locally as XML, and search for a specific keyword.

Search is case-insensitive by default; enable case-sensitive search with --case-sensitive.
Only the <script_contents> section of each Script and the <scripts> section of each Policy is searched.
Outputs provide direct links and context on where the keyword appears, including parameter indices and values for scripts, and a simple policy-level match.
"""
import os
import argparse
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Jamf Pro Scripts & Policies and search for a keyword using Bearer tokens."
    )
    parser.add_argument(
        "--url", required=True,
        help="Base URL of the Jamf Pro server (e.g. https://jamf.example.com)"
    )
    parser.add_argument(
        "--user", required=True,
        help="Jamf Pro API username"
    )
    parser.add_argument(
        "--password", required=True,
        help="Jamf Pro API password"
    )
    parser.add_argument(
        "--keyword", required=True,
        help="Keyword to search within Scripts and Policy parameters"
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Enable case-sensitive search (default: case-insensitive)"
    )
    parser.add_argument(
        "--output", default="output",
        help="Directory to save downloaded XML files (default: output)"
    )
    return parser.parse_args()


def get_bearer_headers(base_url, user, password):
    auth_url = f"{base_url.rstrip('/')}/api/v1/auth/token"
    resp = requests.post(auth_url, auth=HTTPBasicAuth(user, password))
    resp.raise_for_status()
    token = resp.json().get('token')
    if not token:
        raise RuntimeError('Failed to obtain API token')
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/xml'
    }


def fetch_listing(base_url, endpoint, headers):
    url = f"{base_url.rstrip('/')}/JSSResource/{endpoint}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    if endpoint.endswith('ies'):
        tag = endpoint[:-3] + 'y'
    elif endpoint.endswith('s'):
        tag = endpoint[:-1]
    else:
        tag = endpoint
    for item in root.findall(tag):
        id_elem = item.find('id')
        name_elem = item.find('name')
        if id_elem is not None and name_elem is not None:
            yield id_elem.text, name_elem.text


def fetch_detail(base_url, endpoint, resource_id, headers):
    url = f"{base_url.rstrip('/')}/JSSResource/{endpoint}/id/{resource_id}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def save_xml(directory, name, xml_content):
    os.makedirs(directory, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
    filename = os.path.join(directory, f"{safe_name}.xml")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    return filename


def search_script(root, keyword, case_sensitive, base_url):
    script_id_elem = root.find('id')
    script_name_elem = root.find('name')
    if script_id_elem is None or script_name_elem is None:
        return
    script_id = script_id_elem.text
    script_name = script_name_elem.text
    contents = root.find('script_contents')
    text = contents.text or '' if contents is not None else ''
    lines = text.splitlines()
    matches = []
    for idx, line in enumerate(lines, start=1):
        hay = line if case_sensitive else line.lower()
        key = keyword if case_sensitive else keyword.lower()
        if key in hay:
            matches.append((idx, line.strip()))
    if matches:
        print(f"Keyword '{keyword}' found in {script_name} Script")
        print(f"  - URL: {base_url.rstrip('/')}/view/settings/computer-management/scripts/{script_id}?tab=script")
        for num, content in matches:
            print(f"    - Line {num}: {content}")


def search_policy(root, keyword, case_sensitive, base_url):
    general = root.find('general')
    if general is None:
        return
    policy_id_elem = general.find('id')
    policy_name_elem = general.find('name')
    if policy_id_elem is None or policy_name_elem is None:
        return
    policy_id = policy_id_elem.text
    policy_name = policy_name_elem.text
    scripts_section = root.find('scripts')
    if scripts_section is None:
        return
    # Extract all text under <scripts>
    text = ET.tostring(scripts_section, encoding='unicode', method='text')
    hay = text if case_sensitive else text.lower()
    key = keyword if case_sensitive else keyword.lower()
    if key in hay:
        print(f"Keyword '{keyword}' found in {policy_name} Policy")
        print(f"  - URL: {base_url.rstrip('/')}/policies.html?id={policy_id}&o=r")


def process_resources(base_url, endpoint, subdir, headers, keyword, output_dir, case_sensitive):
    print(f"Fetching {endpoint}...")
    for resource_id, name in fetch_listing(base_url, endpoint, headers):
        xml_content = fetch_detail(base_url, endpoint, resource_id, headers)
        directory = os.path.join(output_dir, subdir)
        file_path = save_xml(directory, f"{name}_{resource_id}", xml_content)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError:
            continue
        tag = root.tag.lower()
        if tag == 'script':
            search_script(root, keyword, case_sensitive, base_url)
        elif tag == 'policy':
            search_policy(root, keyword, case_sensitive, base_url)


def main():
    args = parse_args()
    headers = get_bearer_headers(args.url, args.user, args.password)
    process_resources(
        args.url, 'scripts', 'scripts', headers,
        args.keyword, args.output, args.case_sensitive
    )
    process_resources(
        args.url, 'policies', 'policies', headers,
        args.keyword, args.output, args.case_sensitive
    )

if __name__ == '__main__':
    main()
