
import requests, os, signal, json
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
    groups.update({'eh': 26109}) # 
    priority = {
        'eh' : 0,
        'pendulum' : 1, 
        'forsyde radar' : 2, 
        'atlas-hgtd' : 3, 
        'embedded ai-noc' : 4, 
        'automated driving' : 5, 
        'mist seud' : 6,
        'das' : 7, 
        'electric vehicle' : 8
    }

    current_best_priority = len(priority)
    while current_best_priority > 1:
        for name in priority:
            # if current_best_priority == 1:
            #     print("[X] Highest prio was successfully joined, exiting")
            #     break
            # elif priority[name] >= current_best_priority:
            #     continue

            resp = requests.post(
                url=f"{base_url}/groups/{groups[name]}/memberships",
                headers=headers,
                data = { 'user_id': 'self' }
            )
            jsn = resp.json()

            if resp.status_code == 200:
                print(f"[X] {name} ({priority[name]}) -> Joined, find better prio group now")
                current_best_priority = priority[name]
            elif resp.status_code == 403:
                print(f"[!] {name} ({priority[name]}) -> Group not open yet")
            elif resp.status_code == 400:
                print(f"[!] {name} ({priority[name]}) -> {jsn['errors']['group_id'][0]['message']}")
            else:
                print(f"[!] Code is {resp.status_code}, {jsn}")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: (print(), exit(0)))
    main()
