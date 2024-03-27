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
                    event_type = ["payment", "ins_case"][random.randint(0,1)]
                    event_office = ["msk", "spb"][random.randint(0,1)]
                    police_email = random_char(10) + "@" + random_char(5) + "." + random_char(3)
                    if event_type == "payment":
                        payment_value = random.randint(0,1000000)
                        data = json.dumps({'police_email': police_email, 'payment_value': payment_value})
                        print("Generating payment for " + str(payment_value) + " from unit " + event_office)
                    else:
                        data = json.dumps({'police_email': police_email})
                        print("Generating insurance case from unit " + event_office)
                    channel.basic_publish(RMQ_EXCH, event_type+'.'+event_office, data, pika.BasicProperties(content_type='application/json',
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