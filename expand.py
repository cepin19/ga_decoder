import sys
import requests
for line in sys.stdin:
    r=requests.post("http://localhost:5233/search/1/en/cz/",  json=[(line)])
    out=r.json()
    print(';'.join([';'.join(line[word][1]) for line in out for word in line ]))

