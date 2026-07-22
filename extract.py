import urllib.request
import re

try:
    req = urllib.request.Request('https://masterji-19f75.firebaseapp.com/main.js', headers={'User-Agent': 'Mozilla/5.0'})
    js = urllib.request.urlopen(req).read().decode('utf-8')
    strings = re.findall(r'"([^"]{10,100})"', js)
    with open('main_strings.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(set(strings)))
    print("Extracted strings.")
except Exception as e:
    print(e)
