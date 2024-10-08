import os
from datetime import datetime


def find_calendar_date():
    now = datetime.now()
    return now.year, now.month, now.day


def user_contract_folder():
    folder = os.path.join('..')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def checkFile(filename):
    return filename.endswith('.docx')
