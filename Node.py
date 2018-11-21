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



        else:
            raise Exception("Id not valid")
    def passPriviledge(self):
        if self.requestQueue[0] != self.id:
            receiver = self.requestQueue.pop()
            self.send(receiver,P)

node = Node("A")
