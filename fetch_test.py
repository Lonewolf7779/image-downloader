import requests
r = requests.get('http://127.0.0.1:5000/')
print(r.status_code)
print(len(r.text))
print(r.text[:300])
