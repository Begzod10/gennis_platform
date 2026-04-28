import os
import requests
from django.core.files.base import ContentFile

VATS_DOMAIN = "gennis-campus.sip.uz"
VATS_API_KEY = "0db01bec-a886-4dd5-91d7-23e5394cdee4"
VATS_CRM_TOKEN = "aa111"


def save_audio(call):
    if call.audio_url:
        r = requests.get(call.audio_url)

        if r.status_code == 200:
            call.audio.save(
                f"{call.vats_call_id}.mp3",
                ContentFile(r.content),
                save=True
            )
