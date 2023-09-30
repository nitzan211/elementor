import time
from confluent_kafka import Consumer, KafkaError
import boto3
from base64 import b64decode
import os

# Kafka configuration
KAFKA_TOPIC = "cpu_usage"
KAFKA_BROKER = "kafka-controller-0.kafka-controller-headless.default.svc.cluster.local:9092"

# AWS S3 configuration
AWS_REGION = "eu-west-1"
S3_BUCKET_NAME = "elementor-data-candidates-bucket"

# AWS credentials from Kubernetes Secret
AWS_ACCESS_KEY_SECRET_NAME = "aws-secret"
AWS_ACCESS_KEY_SECRET_KEY = "aws_access_key_id"
AWS_SECRET_KEY_SECRET_KEY = "aws_secret_access_key"
K8S_NAMESPACE = "default"

def get_aws_credentials_from_secret():
    # Use Kubernetes client to retrieve the AWS credentials Secret
    from kubernetes import client, config
    config.load_incluster_config() 

    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret(AWS_ACCESS_KEY_SECRET_NAME, K8S_NAMESPACE)
    
    aws_access_key = b64decode(secret.data[AWS_ACCESS_KEY_SECRET_KEY]).decode('utf-8')
    aws_secret_key = b64decode(secret.data[AWS_SECRET_KEY_SECRET_KEY]).decode('utf-8')
    
    return aws_access_key, aws_secret_key

def consume_messages_and_upload_to_s3():
    # Get AWS credentials from Kubernetes Secret
    aws_access_key, aws_secret_key = get_aws_credentials_from_secret()

    # Configure AWS S3 client
    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION
    )

    # Kafka consumer configuration
    kafka_config = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "cpu",
        "auto.offset.reset": "earliest"
    }

    consumer = Consumer(kafka_config)
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print("Reached end of partition")
                else:
                    print(f"Error while consuming from Kafka: {msg.error()}")
            else:
                key = msg.key()
                value = msg.value().decode("utf-8")
                print(f"Received message - Key: {key}, Value: {value}")

                # Upload the message to S3
                s3_key = f"cpu_usage/{int(time.time())}.txt"
                s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=value)
                print(f"Uploaded message to S3: {s3_key}")

    except KeyboardInterrupt:
        print("Consumption stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages_and_upload_to_s3()
