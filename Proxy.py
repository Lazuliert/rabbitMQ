from tree import tree
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_KRaymond',
                         exchange_type='topic')
try:
    while True:
        destination = input("Type a destination\n")
        message = input("Type a message\n")
        message = "Z" + message
        channel.basic_publish(exchange='topic_KRaymond',
                              routing_key=destination,
                              body=message)
        print(" [x] Sent %r:%r" % (destination, message))
except:
    connection.close()


