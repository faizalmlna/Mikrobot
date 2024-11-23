FROM python:3.8

RUN pip install --no-cache-dir python-dotenv==1.0.0 python-telegram-bot paramiko firebase_admin

WORKDIR /app

COPY . .

CMD ["python", "app_v2.py"]
