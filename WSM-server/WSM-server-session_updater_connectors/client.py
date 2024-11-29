import json
import pika

# Configurações do RabbitMQ
RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "pooling"

def send_message(message, queue_name):
    """
    Envia uma mensagem para a fila do RabbitMQ.
    """
    try:
        # Conecta ao RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # Declara a fila antes de enviar a mensagem
        channel.queue_declare(queue=queue_name, durable=True)

        # Envia a mensagem
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # Torna a mensagem persistente
        )

        print(f"Mensagem enviada para a fila '{queue_name}': {message}")
        connection.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem para a fila '{queue_name}': {e}")
        raise

if __name__ == "__main__":
    # Mensagem de teste
    test_message = {
        "action": "notify",
        "hostname": "server01.example.com",
        "user": "johndoe",
        "timezone": "UTC",
        "allowed_schedule": {
            "sunday": [
            { "start": 800, "end": 1200 },
            { "start": 1400, "end": 1800 }
            ],
            "monday": [
            { "start": 900, "end": 1700 }
            ],
            "tuesday": [],
            "wednesday": [
            { "start": 1000, "end": 1500 }
            ],
            "thursday": [],
            "friday": [
            { "start": 800, "end": 1200 }
            ],
            "saturday": []
        },
        "timestamp": "2024-11-21T15:30:00Z",
        "message": "Scheduled maintenance will occur this weekend.",
        "title": "System Notification",
        "options": "Dismiss, Snooze"
        }

    try:
        print("Enviando mensagem de teste para o RabbitMQ...")
        send_message(test_message, RABBITMQ_QUEUE)
        print("Mensagem de teste enviada com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar mensagem de teste: {e}")
