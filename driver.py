
import requests, os, signal
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
    groups.update({'eh': 26109})
    priority = {
        'eh' : 0,
        'pendulum' : 7, 
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
            if current_best_priority == 1:
                print("[X] Highest prio was successfully joined, exiting")
                break
            elif priority[name] >= current_best_priority:
                continue

            jsn = requests.post(
                url=f"{base_url}/groups/{groups[name]}/memberships",
                headers=headers,
                data = { 'user_id': 'self' }
            ).json()

            if 'errors' not in jsn.keys():
                print(f"{name} ({priority[name]}) -> Joined, only try joining groups with prio better than {priority[name]} now")
                current_best_priority = priority[name]
            else:
                def find_message(data):
                    if isinstance(data, dict):
                        return data.get('message') or find_message(data.get('errors', {}))
                    elif isinstance(data, list):
                        return next((find_message(item) for item in data), None)
                    return None
                print(f"[!] {name} ({priority[name]}) -> {find_message(jsn)}")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *_: (print(), exit(0)))
    main()
