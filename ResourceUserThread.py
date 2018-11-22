import threading
import time

from Privilege import Privilege


class ResourceUserThread(threading.Thread):
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)
        self.inCriticalSection = False
        self.privilege = None


    def run(self):
        while True :
            if self.inCriticalSection == False:
                request = input("Type anything to ask for the resource")
                print (request)
            else:
                request = input("type anything to stop using privilege")
                print("input 1", request)


    def enterCriticalSection(self):
        print("entering critical section")
        self.inCriticalSection = True
        self.privilege = Privilege(self.id)
        request = input("type anything to stop using privilege")
        print("input2",request)


thread = ResourceUserThread("A")
thread.start()
time.sleep(5)
thread.enterCriticalSection()
