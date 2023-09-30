FROM python:3

COPY . .

RUN pip install confluent-kafka boto3 kubernetes

ENTRYPOINT ["python", "-u", "consumer-s3.py"]