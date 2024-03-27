import functools
import os
import pika
import time
import socket
import random
import json
import string

RMQ_USER=os.getenv("RMQ_USER", "")
RMQ_PASS=os.getenv("RMQ_PASS", "")
RMQ_HOST=os.getenv("RMQ_HOST", "")
RMQ_EXCH=os.getenv("RMQ_EXCH", "")

def random_char(char_num):
       return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))

def main():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            while True:
                try:
                    police_email = random_char(10) + "@" + random_char(5) + "." + random_char(3)
                    police_value = random.randint(0,1000)
                    message = json.dumps({'police_email': police_email, 'police_value': police_value})
                    police_office = ["msk", "spb"][random.randint(0,1)]
                    print("Generating police registration for value " + str(police_value) + " from unit " + police_office)
                    channel.basic_publish(RMQ_EXCH, 'police.'+police_office, message, pika.BasicProperties(content_type='application/json',
                                           delivery_mode=pika.DeliveryMode.Transient))
                    time.sleep(random.randint(1,30))
                except KeyboardInterrupt:
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