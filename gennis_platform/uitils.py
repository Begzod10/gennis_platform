import requests


def send_subject_server(classroom_server, subject):
    requests.post(f"{classroom_server}/api/get_subjects", headers={'Content-Type': 'application/json'},
                  json={"subject": subject.name})
