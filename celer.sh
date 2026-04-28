#!/bin/bash
source /home/turon/venv/bin/activate

echo "⏱️ Celery Beat ishga tushdi..."
celery -A gennis_platform  beat --loglevel=info &

echo "⚙️ Celery Worker ishga tushdi..."
celery -A gennis_platform  worker --loglevel=info
wait
