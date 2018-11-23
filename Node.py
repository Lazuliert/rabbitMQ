from Privilege import Privilege
import threading
from tree import tree
import pika
import time


class Node(threading.Thread):

    def __init__(self, holderId):

        threading.Thread.__init__(self)
        if holderId in ["A", "B", "C", "D", "E", "F"]:
            self.id = holderId
            self.neighbors = tree[holderId]["neighbors"]
            if holderId == "A" :
                self.holder = "A"
                self.messageSender(".".join(self.neighbors), "I")
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

            self.channel = None
            self.createQueue()



        else:
            raise Exception("Id not valid")

    def run(self):
        """This function is blocking"""
        print(" *** Node " + self.id + " waiting for messages .To exit press CTRL+C")

        def callback(obj, ch, method, properties, body):
            print(" [x] routing_key ; body %r:%r" % (method.routing_key, body))
            obj.receiveManager(body)

        self.channel.basic_consume(lambda ch, method, properties, body: callback(self, ch, method, properties, body),
                                   queue=self.queue_name,
                                   no_ack=True)
        self.channel.start_consuming()


    """
    fonction qui afficher l'état de tous les attributs du node
    """
    def statusPrinter(self, statusMessage = ""):
        if statusMessage != "":
            statusMessage= "Status of node " + self.id
        print(statusMessage)
        print("holder : " + self.holder)
        print("request_q : " + str(self.requestQueue))
        print("using : " + str(self.using))
        print("asked : " + str(self.asked))

    """
    fonction appelée quand il reçoit un message et reroot vers la bonne méthode
    """
    def receiveManager(self, message):
        print("#####Message Received !#####")
        message = message.decode('UTF-8')
        sender = message[0]
        mtype = message[1]
        print("sender" + sender)
        print("mtype" + mtype)
        self.statusPrinter()
        if mtype =="I":
            print("INITIALIZE message from node " + sender + " received")
            self.initialize(sender)
        elif mtype =="P":
            print("PRIVILEGE message from node " + sender + " received")
            self.holder = self.id
            self.assign_privilege()
            self.make_request()
        elif mtype =="Q":
            print("REQUEST message from node " + sender + " received")
            self.requestQueue.add(sender)
            self.assign_privilege()
            self.make_request()
        elif mtype =="S":
            print("RESTART message from node " + sender + " received")
        elif mtype == "W":
            print("ADVISE_1 message from node " + sender + " received")
        elif mtype == "X":
            print("ADVISE_2 message from node " + sender + " received")
        elif mtype == "Y":
            print("ADVISE_3 message from node " + sender + " received")
        elif mtype == "Z":
            print("ADVISE_4 message from node " + sender + " received")
        else:
            print("I DO NOT KNOW")
        print("New status :")
        self.statusPrinter()
        print("#####End of message treatment#####")

    """
    méthode appelée à la reception d'un message initialize
    """
    def initialize(self,sender):
        if self.neighbors == [sender]:
            receivers = []
            for neighbor in self.neighbors :
                if neighbor != sender:
                    receivers.append(neighbor)

            self.messageSender(".".join(receivers), "I")
            self.holder = sender


    def assign_privilege(self):
        if (self.holder == self.id) & (self.using is False) & (self.requestQueue != []):
            self.holder = self.requestQueue.pop(0)
            self.asked = False
            if self.holder == self.id:
                self.using = True
                self.critical_section()
            else:
                self.messageSender(self.holder, "P")

    """function called when entering the critical section"""
    def critical_section(self):
        time.sleep(3)

    """
    méthod creating and connecting to the queue
    """
    def createQueue(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='topic_KRaymond',
                                      exchange_type='topic')
        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue
        binding_key = "#."+ self.id + ".#"
        self.channel.queue_bind(exchange='topic_KRaymond',
                                queue = self.queue_name,
                                routing_key=binding_key)
        print(" *** Node " + self.id + " declared queue with binding key " + binding_key + " .")


    def messageSender(self, destination, message):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange='topic_KRaymond',
                                 exchange_type='topic')

        payload = self.id + message

        channel.basic_publish(exchange='topic_KRaymond',
                              routing_key=destination,
                              body=payload)
        print(" [x] Sent %r:%r" % (destination, payload))
        connection.close()

nodes = []
for nodeId in tree.keys() :
    nodes.append(Node(nodeId))

for node in nodes:
    node.start()

while True:
    request = input("would you like to do something?")
    if len(request) == 1:
        print(request+" will now ask for the privilege/relinquish the privilege")
    else:
        print(request+ "will know be killed/restarted")


