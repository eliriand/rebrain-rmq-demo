from cleantext import replace_emails
import functools
import os
import pika
import time
import socket

RMQ_USER=os.getenv("RMQ_USER", "")
RMQ_PASS=os.getenv("RMQ_PASS", "")
RMQ_HOST=os.getenv("RMQ_HOST", "")
RMQ_QUEUE=os.getenv("RMQ_QUEUE", "pending_to_depers_q")
RMQ_PF_COUNT=os.getenv("RMQ_PF_COUNT", "1")

def depersonate(text):
    return replace_emails(text, replace_with="__EMAIL_HIDDEN__")

def on_message(chan, method_frame, header_frame, body):
    print("Recived depersonation request:")
    print("\tInitial data: " + str(body))
    print("\tDepersonated data: " + depersonate(str(body)))
    chan.basic_ack(delivery_tag=method_frame.delivery_tag)


def main():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    while True:
        try:
            connection = pika.BlockingConnection(parameters)

            channel = connection.channel()
            channel.basic_qos(prefetch_count=int(RMQ_PF_COUNT))

            on_message_callback = functools.partial(
                on_message)
            channel.basic_consume(RMQ_QUEUE, on_message_callback)

            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                channel.stop_consuming()
                connection.close()
                break
        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed by server. Reconnecting...")
            time.sleep(2)
            continue
        except pika.exceptions.AMQPChannelError as err:
            print("Caught a channel error: {}. Stopping...".format(err))
            break
        except socket.gaierror as err:
            print("Could not initialize connection: {}. Retrying...".format(err))
            time.sleep(2)
            continue
        except pika.exceptions.AMQPConnectionError:
            print("Connection lost. Retrying...")
            time.sleep(2)
            continue
    


if __name__ == '__main__':
    main()