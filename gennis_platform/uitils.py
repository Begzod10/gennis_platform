import json

import requests


def send_subject_server(classroom_server, subject):
    requests.post(f"{classroom_server}/api/get_subjects", headers={'Content-Type': 'application/json'},
                  json={"subject": subject.name})


def request(url, method, data=None, headers=None):
    if headers is None:
        headers = {
            'Content-Type': "application/json"
        }
    response = requests.request(method, url, data=json.dumps(data, indent=4), headers=headers)

    return response
