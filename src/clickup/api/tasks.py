import os
import requests

CLICKUP_TEAM_ID = os.getenv('CLICKUP_TEAM_ID')
CLICKUP_API_URL = "https://api.clickup.com/api/v2/team/" + \
    CLICKUP_TEAM_ID + "/time_entries"
CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')
CLICKUP_USER_ID = os.getenv('CLICKUP_USER_ID')


def get_task(task_id: str):

    url = "https://api.clickup.com/api/v2/task/" + task_id

    query = {
        "custom_task_ids": "true",
        "team_id": CLICKUP_TEAM_ID,
        "include_subtasks": "true"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": CLICKUP_API_TOKEN
    }

    task = requests.get(url, headers=headers, params=query)

    return task.json()
