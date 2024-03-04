FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENV MQTT_BROKER_URL=10444491378847629fbd35ecc194ad0b.s1.eu.hivemq.cloud

ENV CUSTOM_BROKER_PORT 8883

CMD ["python3", "app.py"]
