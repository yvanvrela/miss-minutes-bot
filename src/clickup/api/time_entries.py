import os
import requests

CLICKUP_TEAM_ID = os.getenv('CLICKUP_TEAM_ID')
CLICKUP_API_URL = "https://api.clickup.com/api/v2/team/" + \
    CLICKUP_TEAM_ID + "/time_entries"
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')
CLICKUP_USER_ID = os.getenv('CLICKUP_USER_ID')


def add_time_entry(task_id: str, description: str, start_time: int, duration: int):
    query = {
        "custom_task_ids": "true",
        "team_id": CLICKUP_TEAM_ID
    }

    payload = {
        "description": description,
        "tags": [
            {
                "name": "from quicktimerbot",
                "tag_bg": "#BF55EC",
                "tag_fg": "#FFFFFF"
            }
        ],
        "start": start_time,  # microseconds
        "billable": False,  # Facturable
        "duration": duration,  # microseconds
        "assignee": int(CLICKUP_USER_ID),
        "tid": task_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": CLICKUP_API_TOKEN
    }

    response = requests.post(CLICKUP_API_URL, json=payload,
                             headers=headers, params=query)

    data = response.json()

    return data
