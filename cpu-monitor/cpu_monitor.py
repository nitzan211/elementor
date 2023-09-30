import time
import psutil
from confluent_kafka import Producer

# Kafka configuration
KAFKA_TOPIC = "cpu_usage"  
KAFKA_BROKER = "kafka-controller-0.kafka-controller-headless.default.svc.cluster.local:9092"

def monitor_cpu_and_send_to_kafka(interval_seconds=60):
    # Kafka producer configuration
    kafka_config = {
        "bootstrap.servers": KAFKA_BROKER
    }

    producer = Producer(kafka_config)

    try:
        while True:
            cpu_usage = psutil.cpu_percent(interval=None)
            message = f"CPU Usage: {cpu_usage}%"
            producer.produce(KAFKA_TOPIC, key="cpu_usage", value=message)
            producer.flush()
            print(message)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitoring_interval = 60

    monitor_cpu_and_send_to_kafka(monitoring_interval)
