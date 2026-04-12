import os
import requests
from django.core.files.base import ContentFile

VATS_DOMAIN = "https://gennis-campus.sip.uz/crmapi/v1"
VATS_API_KEY = "6976dcaa-ddb8-4417-8192-ff22ba596d45"
VATS_CRM_TOKEN = "123"


def save_audio(call):
    if call.audio_url:
        r = requests.get(call.audio_url)

        if r.status_code == 200:
            call.audio.save(
                f"{call.vats_call_id}.mp3",
                ContentFile(r.content),
                save=True
            )
