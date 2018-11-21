import pika
from tree import tree
import string
import pika


class Node :
    def __init__(self, id):
        if id in ["A", "B", "C", "D", "E", "F"]:
            self.id = id
            self.neighbors = tree[id]["neighbors"]
            if id == "A" :
                self.holder = "A"
                self.send(".".join(self.neighbors), "I")
            else:
                self.holder = ""


            #True if your using the resource False if not --> initialized at False
            #Can be true if and only if holder=self.id
            self.using = False

            #contains the ids of all the node from whom the node received a request that was not satisfied
            self.requestQueue = []

            #True when I am the non priviledged holder and I have already sent a request message to the current holder.
            # False otherwise.
            self.asked = False

            self.createConnection(self)

        else:
            raise Exception("Id not valid")
    def passPriviledge(self):
        if self.requestQueue[0] != self.id:
            receiver = self.requestQueue.pop()
            self.send(receiver,P)



    def createConnection(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='topic_KRaymond',
                                 exchange_type='topic')
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        binding_key = "#."+ self.id +".#"
        self.channel.queue_bind(exchange='topic_KRaymond',
                           queue = queue_name,
                           routing_key=binding_key)
        print(" *** Node " + self.id +" declared queue with binding key " + binding_key + " .")


        def callback(ch, method, properties, body):
            print(" [x] routing_key ; body %r:%r" % (method.routing_key, body))

        self.channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)
        return self.channel

    def beginReceiver(self):
        """This function is blocking"""
        print(" *** Node " + self.id +" waiting for messages with binding key " + binding_key + " .To exit press CTRL+C")


    def messageSender(self,destination, message):

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        payload = self.id + message
        channel.exchange_declare(exchange='topic_KRaymond',
                                 exchange_type='topic')

        channel.basic_publish(exchange='topic_logs',
                              routing_key=destination,
                              body=payload)
        print(" [x] Sent %r:%r" % (destination, payload))
        connection.close()

node = Node("A")
