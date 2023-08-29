
import requests, os, signal
from fuzzywuzzy import process
from dotenv import load_dotenv

def main():
    base_url = 'https://canvas.kth.se/api/v1'
    course_id = '41739'

    load_dotenv()
    tkn = os.getenv('BEARER_TOKEN')
    headers = {
        'Authorization': f'Bearer {tkn}'
    }

    response = requests.get(
        url=f"{base_url}/courses/{course_id}/groups",
        headers=headers
    )
    resp_json = response.json()

    groups = {item['name'].lower(): item['id'] for item in resp_json}
    groups.update({'eh': 26109}) # test: group that is closed for sure
    priorities = {
        'eh' : 0,
        'pendulum' : 1, 
        'forsyderadar' : 2, 
        'atlas-hgtd' : 3, 
        'embeddedai-noc' : 4, 
        'automateddriving' : 5, 
        'mistseud' : 6,
        'das' : 7, 
        'electricvehicle' : 8
    }

    current_best_priority = len(priorities)
    while current_best_priority > 1:
        for name in priorities:
            if current_best_priority == 1:
                print("[S] Highest prio was successfully joined, exiting")
                break
            elif priorities[name] >= current_best_priority:
                continue

            group, _ = process.extractOne(name, groups.keys())
            
            # API ref: Update a membership
            # API ref: Get groups for a course (given by id)
            # https://canvas.instructure.com/doc/api/groups.html#method.groups.context_index
            resp = requests.post(
                url=f"{base_url}/groups/{groups[group]}/memberships",
                headers=headers,
                data = { 'user_id': 'self' }
            )
            jsn = resp.json()

            if resp.status_code == 200:
                print(f"[S] {group} ({priorities[name]}) -> Joined, find better prio group now")
                current_best_priority = priorities[name]
            elif resp.status_code == 403:
                print(f"[!] {group} ({priorities[name]}) -> Group not open yet")
            elif resp.status_code == 400:
                msg = jsn['errors']['group_id'][0]['message']
                print(f"[!] {group} ({priorities[name]}) -> {msg}")
            else:
                print(f"[!] Code is {resp.status_code}, {jsn}")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: (print(), exit(0)))
    main()
