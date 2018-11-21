from tree import tree


class Node :
    def __init__(self, id):
        if id in ["A", "B", "C", "D", "E", "F"]:
            self.id = id
            self.neighbors = tree[id]["neighbors"]
            if id == "A" :
                self.holder = "A"
            else:
                self.holder = ""

            #True if your using the resource False if not --> initialized at False
            #Can be true if and only if holder=self.id
            self.using = False

            #contains the ids of all the node from whom the node received a request that was not satisfied
            self.requestQueue = []

            #True when non priviledged holder has send a request message to the current holder. False otherwise.
            self.asked = False



        else:
            raise Exception("Id not valid")


node = Node("A")
print(node.neighbors)