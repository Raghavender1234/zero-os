import urllib.request
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    url = 'https://api.github.com/repos/Raghavender1234/zero-os/actions/runs'
    req = urllib.request.Request(url, headers={'User-Agent': 'ZeroOS-Inspector'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            runs = data.get('workflow_runs', [])
            if not runs:
                print('No runs found.')
                return
            latest = runs[0]
            print(f"Latest Run: ID {latest['id']} | Status: {latest['status']} | Conclusion: {latest['conclusion']}")
            print(f"Commit: {latest['head_sha'][:7]} - {latest['head_commit']['message']}")
            print(f"URL: {latest['html_url']}")

            req_jobs = urllib.request.Request(latest['jobs_url'], headers={'User-Agent': 'ZeroOS-Inspector'})
            with urllib.request.urlopen(req_jobs) as j_resp:
                j_data = json.loads(j_resp.read().decode('utf-8'))
                for job in j_data.get('jobs', []):
                    print(f"\nJob: {job['name']} ({job['status']})")
                    for step in job.get('steps', []):
                        icon = "✅" if step.get('conclusion') == 'success' else ("❌" if step.get('conclusion') == 'failure' else "⏳")
                        print(f"  {icon} Step {step['number']}: {step['name']} [{step['status']}]")
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
