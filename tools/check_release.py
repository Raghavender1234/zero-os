import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    url = 'https://api.github.com/repos/Raghavender1234/zero-os/releases'
    req = urllib.request.Request(url, headers={'User-Agent': 'ZeroOS-Inspector'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"Total Releases: {len(data)}")
            for r in data:
                print(f"Release Name: {r.get('name')}")
                print(f"Tag: {r.get('tag_name')}")
                print(f"URL: {r.get('html_url')}")
                assets = r.get('assets', [])
                print(f"Assets Count: {len(assets)}")
                for a in assets:
                    print(f"  • {a['name']} ({a['size']} bytes)")
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
