from __future__ import annotations

import json
import logging
import os
import pika

def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    rabbitmq_url = os.getenv("ALL_IN_ONE_RABBITMQ_URL", "amqp://all_in_one:local-development-only@localhost:5672/")
    exchange_name = os.getenv("ALL_IN_ONE_OUTBOX_EXCHANGE", "all-in-one.domain")
    queue_name = "notification.worker.queue"
    
    try:
        parameters = pika.URLParameters(rabbitmq_url)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Bind to relevant events
        routing_keys = ["business.dispute.resolved", "business.dispute.closed", "support.ticket.created", "marketplace.dispute.created"]
        for key in routing_keys:
            channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=key)
            
        def callback(ch, method, properties, body):
            try:
                event = json.loads(body.decode('utf-8'))
                routing_key = method.routing_key
                logging.info(f"Received event {routing_key}: {event.get('id')}")
                
                # Mock sending notification
                user_id = event.get('user_id', 'unknown')
                payload = event.get('payload', {})
                logging.info(f"Sending notification to user {user_id} regarding case for order: {payload.get('order_id')}")
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        
        logging.info("Notification worker started, waiting for messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Worker stopped by user.")
        return 0
    except Exception as e:
        logging.error(f"Worker failed: {e}")
        return 1
        
    return 0
