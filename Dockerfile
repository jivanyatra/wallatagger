FROM python:3.11.9-alpine

COPY . .

RUN pip install -r requirements.txt

# figure out crontab/ crond/ tail log