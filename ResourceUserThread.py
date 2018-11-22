import threading

class ResourceUserThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)


    def run(self):
        while True :
            request = input("Type anything to ask for the resource")
            print (request)

