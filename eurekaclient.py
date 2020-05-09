import requests
import socket
import threading
import signal,time
import sys

class EurekaClient(threading.Thread):
    def __init__(self, eurekaServerUrl, appname, hostport,renewalInterval=60):
        threading.Thread.__init__(self)
        self.daemon = False
        self.event = threading.Event()
        self.url = eurekaServerUrl
        self.appname = appname
        self.hostport = hostport
        self.renewalInterval = renewalInterval
        self.registrationPayload = {
            "instance": {
                "hostName": socket.gethostbyname(socket.gethostname()),
                "instanceId": "{ip}-{appname}-{hostport}".format(ip=socket.gethostbyname(socket.gethostname()),appname=self.appname,hostport=self.hostport),
                "vipAddress": str(self.appname),
                "app": "{}".format(self.appname.upper()),
                "ipAddr": socket.gethostbyname(socket.gethostname()),
                "status": "UP",
                "port": {
                    "$": self.hostport,
                    "@enabled": "true"
                },
                "dataCenterInfo": {
                    "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                    "name": "MyOwn"
                }
            }
        }
        
    def registerWithServer(self):
        eurekaRegistrationUrl = "{url}/eureka/apps/{appname}".format(url=self.url,appname=self.appname)
        print("Registering at:{}".format(eurekaRegistrationUrl))
        try:
            registrationResponse = requests.post(eurekaRegistrationUrl,json=self.registrationPayload,headers={"Content-Type":"application/json"})
            print(registrationResponse.status_code)
            if(registrationResponse.status_code == 204):
                print("Successfully Registered")
                self.start()
            else:
                print("Couldnot Register")
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def run(self):
        while not self.event.wait(self.renewalInterval):
            self.sendHeartBeat()
    
    def sendHeartBeat(self): 
        print("Sending heartbeat")
        heartbeatUrl =  "{url}/eureka/apps/{appname}/{instanceId}".format(url=self.url,appname=self.appname,instanceId=self.registrationPayload["instance"]["instanceId"])
        print("Sending heartbeat to {}".format(heartbeatUrl))
        try:
            heartbeatResponse = requests.put(heartbeatUrl,headers={"Content-Type":"application/json"})
            print(heartbeatResponse.status_code)
            if(heartbeatResponse.status_code != 200):
                print("Error in sending heartbeat:{statuscode}".format(heartbeatResponse.status_code))
                self.unregisterFromServer()
            else:
                print("Successfully sent heartbeat")
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            self.unregisterFromServer()

    
    def unregisterFromServer(self):
        unregisterUrl =  "{url}/eureka/apps/{appname}/{instanceId}".format(url=self.url,appname=self.appname,instanceId=self.registrationPayload["instance"]["instanceId"])
        print("Trying to unregister {}".format(unregisterUrl))
        try:
            heartbeatResponse = requests.delete(unregisterUrl,headers={"Content-Type":"application/json"})
            if(heartbeatResponse.status_code != 200):
                print("Error in Unregistering:{statuscode}".format(heartbeatResponse.status_code))
            else:
                print("Successfully unregistered")
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        self.event.set()
        self.join()
        sys.exit(0)
    def killSignalHandler(self,signum, frame):
        print("Kill Signal Called")
        self.unregisterFromServer()



def sigTerm(signal,frame):
    print("You have ended")



def startEurekaClient(serverUrl,appname,port,renewalInterval=60):
    client = EurekaClient(serverUrl,appname,port,renewalInterval)
    signal.signal(signal.SIGTERM, client.killSignalHandler)
    signal.signal(signal.SIGINT, client.killSignalHandler)
    client.registerWithServer()
    #client.start()




if __name__=="__main__":
    startEurekaClient("http://username:password@localhost:8761","TEST-APP","8007")
    # client = EurekaClient("http://trackereureka:Covid19api@localhost:8761","TEST-APP","8007")
    # signal.signal(signal.SIGTERM, signal_handler)
    # signal.signal(signal.SIGINT, signal_handler)
    # client.registerWithServer()
    # event =  client.getEvent()
    # client.start()
    # while True:
    #     try:
    #         time.sleep(1)     
    #     except ProgramKilled:
    #         #event.set()
    #         client.unregisterFromServer()
    #         break

