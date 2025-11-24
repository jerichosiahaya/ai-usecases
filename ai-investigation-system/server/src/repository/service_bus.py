import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from loguru import logger


class ServiceBusRepository:
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
