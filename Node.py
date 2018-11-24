from Privilege import Privilege
from ResourceUserThread import ResourceUserThread
from tree import tree
import threading
import pika
from time import sleep

class Node(threading.Thread):


    def __init__(self, holder_id):

        threading.Thread.__init__(self)

        if holder_id in ["A", "B", "C", "D", "E", "F"]:
            self.id = holder_id
            self.neighbors = tree[holder_id]["neighbors"]
            if holder_id == "A" :
                self.holder = "A"
                self.send_message(".".join(self.neighbors), "I")
            else:
                self.holder = ""


            #True if your using the resource False if not --> initialized at False
            #Can be true if and only if holder=self.id
            self.using = False

            #contains the ids of all the node from whom the node received a request that was not satisfied
            self.request_queue = []

            #True when I am the non priviledged holder and I have already sent a request message to the current holder.
            # False otherwise.
            self.asked = False

            self.channel = None
            self.create_queue()

            self.privilege=None

            self.stopped = False
            self.recovering = False
            self.holder_advices={} # store "Am I the holder for [sender] ?"
            self.asked_advices={}  # store "Is asked true for [sender] ?"
            self.rq_in_advices={}  # store "Am I in the request queue for [sender] ?"



        else:
            raise Exception("Id not valid")

    """
    method inherited and overloaded from class Thread. Called when the thread starts.
    """
    def run(self):
        """This function is blocking"""
        print(" *** Node " + self.id + " waiting for messages .To exit press CTRL+C")

        def callback(obj, ch, method, properties, body):
            print(" [x] routing_key ; body %r:%r" % (method.routing_key, body))
            obj.receive_manager(body)

        self.channel.basic_consume(lambda ch, method, properties, body: callback(self, ch, method, properties, body),
                                   queue=self.queue_name,
                                   no_ack=True)
        self.channel.start_consuming()

    """
    fonction qui afficher l'état de tous les attributs du node
    """
    def status_printer(self, status_message =""):
        if status_message != "":
            status_message= "Status of node " + self.id
        print(status_message)
        print("holder : " + self.holder)
        print("request_q : " + str(self.request_queue))
        print("using : " + str(self.using))
        print("asked : " + str(self.asked))


    """
    fonction appelée quand il reçoit un message et reroot vers la bonne méthode
    """
    def receive_manager(self, message):
        print("#####Message Received !#####")
        message = message.decode('UTF-8')
        sender = message[0:-1]
        mtype = message[-1]
        print("sender" + sender)
        print("mtype" + mtype)
        if self.stopped == False :
            if self.recovering == False:
                #self.status_printer()
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
                    self.request_queue.append(sender)
                    self.assign_privilege()
                    self.make_request()
                elif mtype =="S":
                    print("RESTART message from node " + sender + " received")
                    self.make_advice(sender)
                elif mtype in ['W', 'X,', 'Y', 'Z']:
                    print("ADVISE Message received. This is not normal")

                else:
                    print("I DO NOT KNOW")
                #print("New status :")
                #self.status_printer()
                #print("#####End of message treatment#####")
            else:
                if mtype =="I":
                    print("INITIALIZE message from node " + sender + " received")
                    self.initialize(sender)
                elif mtype =="P":
                    print("PRIVILEGE message from node " + sender + " received")
                    self.holder = self.id
                    #self.assign_privilege()
                    #self.make_request()
                elif mtype =="Q":
                    print("REQUEST message from node " + sender + " received")
                    self.request_queue.append(sender)
                    #self.assign_privilege()
                    #self.make_request()
                elif mtype =="S":
                    print("RESTART message from node " + sender + " received")
                elif mtype in ['W', 'X', 'Y', 'Z']:
                    print("Advice message :" +mtype)
                    self.store_advice(sender, mtype)
                else:
                    print("I DO NOT KNOW")
                #print("New status :")
                #self.status_printer()
                #print("#####End of message treatment#####")
        else :
            print("The node " + self.id + " is currently stopped. It has ignored this message")

    def make_request(self):
        if (self.holder != self.id) & (self.request_queue != []) & (self.asked == False):
            self.send_message(self.holder, "Q")
            self.asked = True


    """
    méthode appelée à la reception d'un message initialize
    """
    def initialize(self, sender):
        self.holder = sender
        if self.neighbors != [sender]:
            receivers = []
            for neighbor in self.neighbors :
                if neighbor != sender:
                    receivers.append(neighbor)

            self.send_message(".".join(receivers), "I")

    def store_advice(self, sender, advice):
        if advice == 'W':
            self.holder_advices[sender] = self.id
            self.asked_advices[sender] = False
        elif advice == 'X':
            self.holder_advices[sender] = self.id
            self.asked_advices[sender] = True
        elif advice=='Y':
            self.holder_advices[sender]= sender
            self.rq_in_advices[sender] = False
        elif advice == 'Z':
            self.holder_advices[sender]= sender
            self.rq_in_advices[sender] = True
        else:
            print("Unknown advice")

        if len(self.holder_advices) == len(self.neighbors): # All advices received
            print("Reconstructing data...")
            if self.holder == "": # Je n'ai pas recu le message PRIVILEGE entre temps
                holder_flag = True
                for key in self.holder_advices:
                    if self.holder_advices[key]!=self.id:
                        holder_flag = False
                        self.holder = key
                if holder_flag:
                    self.holder = self.id
            # Si je suis le holder pour tous mes voisins, je suis le holder
            # si pour un voisin je ne suis pas le holder, c'est lui le holder

            if self.holder == self.id:
                self.asked = False
            else:
                if self.rq_in_advices[self.holder]:
                    self.asked = True
                else :
                    self.asked = False
            # Si je suis le holder, asked est forcement faux
            # Si je ne suis pas le holder, et que je suis dans la queue de
            # requetes du holder, alors asked = True

            for key in self.asked_advices:
                if self.asked_advices[key] == True:
                    self.request_queue.append(key)
            # Si le noeud X me prends pour le holder, alors il m'as envoye l'etat
            # de son asked. Si son asked est vrai, alors il veut le privilege
            # et je le met dans ma liste de requetes
            self.recovering = False
            self.status_printer("Status after recovering")
            self.assign_privilege()
            self.make_request()
            # Maintenant que je possede toutes les infos, je peux reprendre le
            # fonctionnement normal

    def make_advice(self, destination):
        if (self.holder==destination)&(self.asked==False):
            self.send_message(destination, 'W')
        elif (self.holder==destination)&(self.asked==True):
            self.send_message(destination, "X")
        elif (self.holder!=destination)&(destination not in self.request_queue):
            self.send_message(destination, "Y")
        elif (self.holder!=destination)&(destination in self.request_queue):
            self.send_message(destination, "Z")
        else:
            print("This is not normal. Node " + self.id + " was not able to give advice")

    def stop(self):
        self.stopped = True
        self.holder = ""
        self.using = False
        self.request_queue = []
        self.asked = False

    def restart(self):
        self.stopped = False
        self.recovering = True
        sleep(2) # wait for 2 seconds so all messages sent before failure have been received
        self.send_message(".".join(self.neighbors), "S")

    def assign_privilege(self):
        if (self.holder == self.id) & (self.using is False) & (self.request_queue != []):
            self.holder = self.request_queue.pop(0)
            self.asked = False
            if self.holder == self.id:
                self.using = True
                self.critical_section()
            else:
                self.send_message(self.holder, "P")

    """function called when entering the critical section"""
    def critical_section(self):
        self. privilege = Privilege(self.id)

    """
    méthod creating and connecting to the queue
    """
    def create_queue(self):
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


    def send_message(self, destination, message):
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

    def exit_critical_section(self):
        self.privilege.deconnection()
        self.using = False
        self.assign_privilege()
        self.make_request()

    def make_wish(self):
        #le noeud se met lui-même dans la queue
        self.request_queue.append(self.id)
        #utilise assign_privilege
        self.assign_privilege()
        #utilise make_request
        self.make_request()


nodes = {}
for nodeId in tree.keys() :
    if nodeId != "A":
        nodes[nodeId] = Node(nodeId)
        nodes[nodeId].daemon = True
        nodes[nodeId].start()

nodes["A"] = Node("A")
nodes["A"].daemon = True
nodes["A"].start()


while True:
    request = input("would you like to do something?")
    if request in ["A", "B", "C", "D", "E", "F"]:
        node = nodes[request]
        node.status_printer()
        if node.stopped :
            print("This node is stopped. It will do nothing")
        elif node.using:
            print(request + " will know stop using the privilege")

            node.exit_critical_section()
        else:
            node.status_printer()
            print(request + " will now ask for the privilege for himself" )
            node.make_wish()


    elif request[0] == "C" and len(request)==3:
        holder_id = request[2]
        node = nodes[holder_id]
        node.status_printer()
        if node.stopped == False:
            print("node " + holder_id + " will now be stopped")
            node.stop()
        else:
            print("node " + holder_id + " will now restart")
            node.restart()

    else:
        print("Invalid command")


