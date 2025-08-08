#!/bin/bash
source /home/ubuntu/gennis_website/venv/bin/activate

echo "⏱️ Celery Beat ishga tushdi..."
celery -A config beat --loglevel=info &

echo "⚙️ Celery Worker ishga tushdi..."
celery -A config worker --loglevel=info
wait
