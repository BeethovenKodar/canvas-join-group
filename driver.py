
import requests, os, signal, time
from fuzzywuzzy import process
from dotenv import load_dotenv

def main():
    load_dotenv()

    base_url = 'https://canvas.kth.se/api/v1'
    token = { 'Authorization': f'Bearer {os.getenv("BEARER_TOKEN")}' }

    # API ref: Get groups for a course (given by id)
    # https://canvas.instructure.com/doc/api/groups.html#method.groups.context_index
    response = requests.get(
        url=f"{base_url}/courses/41739/groups", # IL2232 HT23 Embedded Systems Design Project
        headers=token
    )
    resp_json = response.json()

    groups = {
        item['name'].lower(): item['id'] 
        for item in resp_json
    }

    priorities = [
        process.extractOne(hardcoded_name, groups.keys())[0]
        for hardcoded_name in [
            'pendulum', 
            'forsyde radar', 
            'atlas-hgtd', 
            ' embedded ai-noc (task 5)', 
            'automateddriving',
            'das', 
            'embedded ai-noc (task 1, 2, 3, 4)',
            'mistseud',
            'electric vehicle'
        ]
    ]

    current_best_priority = len(priorities)
    session = requests.Session()

    while current_best_priority > 0:
        for prio, group in enumerate(priorities):
            if prio >= current_best_priority: # only attempt higher prio groups than current
                continue

            resp = requests.Response()
            resp.status_code = 403
            # poll until group is open
            while resp.status_code == 403: # CLOSED (unauthorized)
                # API ref: Update a membership (join group)
                # https://canvas.instructure.com/doc/api/groups.html#method.groups.context_index
                resp = session.post(
                    url=f"{base_url}/groups/{groups[group]}/memberships",
                    headers=token,
                    data = { 'user_id': 'self' }
                )
                print(f"[!] {group} (prio {prio}) -> Group not open yet")
                # time.sleep(0.1)

            jsn = resp.json()
            match resp.status_code:
                case 200 : print(f"[S] {group} (prio: {prio}) -> Joined, find better prio group now") # OK
                case 400 : print(f"[!] {group} (prio: {prio}) -> {jsn['errors']['group_id'][0]['message']}") # ERROR
                case _   : print(f"[!] {group} (prio: {prio}) -> Returned {resp.status_code}: {jsn}") # UNEXPECTED
            if resp.status_code == 200:
                current_best_priority = prio

    print("[S] Highest prio group was successfully joined, exiting")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: (print(), exit(0)))
    main()
