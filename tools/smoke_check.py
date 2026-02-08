import os
import sys
import requests

# Read base URL from environment to avoid hardcoded development addresses.
BASE = os.environ.get('BASE_URL')
if not BASE:
    print('Please set BASE_URL environment variable to the site root (e.g. https://example.com)')
    sys.exit(2)

urls = [BASE.rstrip('/') + '/', BASE.rstrip('/') + '/app']
for u in urls:
    print('Fetching', u)
    try:
        r = requests.get(u, timeout=10)
        print('Status:', r.status_code)
        print('Headers:')
        for k, v in r.headers.items():
            print(f'{k}: {v}')
        print('\nBody preview:\n')
        print(r.text[:800])
    except Exception as e:
        print('Error:', e)
    print('\n' + ('-' * 30) + '\n')
