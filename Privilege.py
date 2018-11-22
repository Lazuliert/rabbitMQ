class Privilege :
    inUse = False
    path = []

    def __init__(self, holder):
        self.holder = ""
        if Privilege.inUse == False :
            print("The resource is being used by " + holder)
            self.holder = holder
            Privilege.path.append(holder)
            Privilege.inUse=True
        else:
            raise Exception("The resource is already being used by " + Privilege.path[-1])
    def deconnexion(self):
        print(self.holder+" se déconnecte")
        Privilege.inUse = False

print("A demande le privilège")
print(Privilege.inUse)
privilege = Privilege("A")
privilege.deconnexion()
print("B demande le privilège")
privilege = Privilege("B")
print(Privilege.path)