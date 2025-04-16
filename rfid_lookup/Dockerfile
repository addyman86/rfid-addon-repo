FROM python:3.11-slim

WORKDIR /app
COPY rfid_lookup.py .

RUN pip install --no-cache-dir paho-mqtt mariadb

CMD ["python", "rfid_lookup.py"]
