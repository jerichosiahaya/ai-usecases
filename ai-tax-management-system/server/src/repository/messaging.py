import json
import pika
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from loguru import logger

class AzureServiceBusRepository:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        if not connection_string:
            logger.warning("SERVICE_BUS_CONNECTION_STRING is not set")
        self.client = ServiceBusClient.from_connection_string(connection_string)
    
    def send_message(self, queue_name: str, message_data: dict):
        try:
            sender = self.client.get_queue_sender(queue_name)
            msg = ServiceBusMessage(body=json.dumps(message_data))
            sender.send_messages(msg)
            logger.info(f"Message sent to queue {queue_name}: {message_data}")
        except Exception as e:
            logger.error(f"Error sending message to queue {queue_name}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            raise

class RabbitMQRepository:
    def __init__(self, host: str = "localhost", port: int = 5672, username: str = "guest", password: str = "guest"):

        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password)
        )
        logger.info(f"RabbitMQ repository initialized for {host}:{port}")
    
    def send_message(self, queue_name: str, message_data: dict):
        """
        Send a message to a RabbitMQ queue.
        
        Args:
            queue_name: Name of the queue to send message to
            message_data: Dictionary to send as JSON message
        """
        connection = None
        try:
            # Create connection
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            
            # Declare queue (creates if doesn't exist)
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Send message
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            
            logger.info(f"Message sent to RabbitMQ queue {queue_name}: {message_data}")
            
        except Exception as e:
            logger.error(f"Error sending message to RabbitMQ queue {queue_name}: {str(e)}")
            raise
        finally:
            if connection and connection.is_open:
                connection.close()
