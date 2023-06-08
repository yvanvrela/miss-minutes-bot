import os
import requests

CLICKUP_TEAM_ID = os.getenv('CLICKUP_TEAM_ID')
CLICKUP_API_URL = "https://api.clickup.com/api/v2/team/" + \
    CLICKUP_TEAM_ID + "/time_entries"
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')


def add_time_entry(task_id: str, description: str, start_time: int, duration: int, assignee: int, remote=True):
    query = {
        "custom_task_ids": "true",
        "team_id": CLICKUP_TEAM_ID
    }

    tags = [
        {
            "name": "from quicktimerbot",
            "tag_bg": "#BF55EC",
            "tag_fg": "#FFFFFF"
        }
    ]

    if remote:
        tags.append(
            {
                "name": "remoto",
                "tag_bg": "#800000",
                "tag_fg": "#800000"
            }
        )

    payload = {
        "description": description,
        "tags": tags,
        "start": start_time,  # microseconds
        "billable": True,  # Facturable
        "duration": duration,  # microseconds
        "assignee": assignee,
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
