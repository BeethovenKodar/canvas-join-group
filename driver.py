
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
    # groups.update({'eh': 26109}) # test: group that is closed for sure
    priorities = [
        # 'eh',
        'pendulum', 
        'forsyderadar', 
        'atlas-hgtd', 
        'embeddedai-noc', 
        'automateddriving', 
        'mistseud',
        'das', 
        'electricvehicle'
    ]

    current_best_priority = len(priorities)
    while current_best_priority > 1:
        for prio, name in enumerate(priorities):
            if current_best_priority == 0:
                print("[S] Highest prio was successfully joined, exiting")
                break
            elif prio >= current_best_priority:
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
                print(f"[S] {group} ({prio}) -> Joined, find better prio group now")
                current_best_priority = prio
            elif resp.status_code == 403:
                print(f"[!] {group} ({prio}) -> Group not open yet")
            elif resp.status_code == 400:
                msg = jsn['errors']['group_id'][0]['message']
                print(f"[!] {group} ({prio}) -> {msg}")
            else:
                print(f"[!] Code is {resp.status_code}, {jsn}")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: (print(), exit(0)))
    main()
