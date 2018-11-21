from tree import tree


class Node :
    def __init__(self, id):
        if id in ["A", "B", "C", "D", "E", "F"]:
            self.id = id
            self.neighbors = tree[id]["neighbors"]
        else:
            raise Exception("Id not valid")


node = Node("A")
print(node.neighbors)