"""
Score CSV data using a MAS-deployed model via the MAS REST API.
"""

import argparse
import json
import logging

import pandas as pd
import requests
import urllib3

from src.utils.auth_utils import get_token

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def list_modules(host, token):
    url = f"{host}/microanalyticScore/modules/"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    return [item['name'] for item in r.json().get('items', [])]


def get_step_id(host, token, module):
    url = f"{host}/microanalyticScore/modules/{module}/steps"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    items = r.json().get('items', [])
    print(f"=== Available steps for module '{module}' ===")
    for step in items:
        print(f"Step ID: {step['id']}")
        if 'inputs' in step:
            print("Inputs:")
            for inp in step['inputs']:
                print(f"  - {inp.get('name', 'N/A')}: {inp.get('type', 'N/A')}")
        # Print the full step definition for debugging
        print(f"Full step definition: {json.dumps(step, indent=2)}")
    print("==========================================")
    
    for step in items:
        if step['id'].lower() == 'score':
            return step['id']
    if not items:
        raise RuntimeError(f"No steps found for module '{module}'")
    return items[0]['id']


def score_records(host, token, module, records):
    step = get_step_id(host, token, module)
    url = f"{host}/microanalyticScore/modules/{module}/steps/{step}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type':  'application/vnd.sas.microanalytic.module.step.input+json',
        'Accept':        'application/vnd.sas.microanalytic.module.step.output+json'
    }

    # Process each record individually since MAS expects single record format
    all_results = []
    for rec in records:
        inputs = [{'name': k.lower(), 'value': v} for k, v in rec.items()]
        payload = {'inputs': inputs}
        
        r = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        if not r.ok:
            print("=== MAS scoring request payload ===")
            print(json.dumps(payload, indent=2))
            print("=== MAS response ===")
            print(r.status_code, r.text)
            r.raise_for_status()
        
        all_results.append(r.json())
    
    return all_results


def main():
    p = argparse.ArgumentParser("Score CSV via MAS REST API")
    p.add_argument('-H', '--host',       required=True, help='Viya host, e.g. https://create.demo.sas.com')
    p.add_argument('-m', '--module',     required=True, help='MAS module name')
    p.add_argument('-i', '--input-csv',  required=True, help='Path to input CSV file')
    p.add_argument('-o', '--output-csv', required=True, help='Path to output CSV file')
    args = p.parse_args()

    token = get_token()
    mods = list_modules(args.host, token)
    logger.info("Available modules: %s", mods)

    df = pd.read_csv(args.input_csv)
    records = df.to_dict(orient='records')
    scored = score_records(args.host, token, args.module, records)

    out = []
    for item in scored:
        row = {o['name']: o['value'] for o in item.get('outputs', [])}
        # include inputs if desired:
        for i in item.get('inputs', []):
            row[i['name']] = i['value']
        out.append(row)

    pd.DataFrame(out).to_csv(args.output_csv, index=False)
    logger.info("Scored data written to %s", args.output_csv)


if __name__ == '__main__':
    main()
