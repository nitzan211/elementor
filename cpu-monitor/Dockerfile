FROM python:3

COPY . .

RUN pip install psutil confluent-kafka

ENTRYPOINT ["python", "-u", "cpu_monitor.py"]