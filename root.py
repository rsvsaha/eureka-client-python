from eurekaclient import startEurekaClient
from flask import Flask,request

startEurekaClient("http://username:password@localhost:8761","TEST-APP","8007")
app = Flask(__name__)

@app.route("/test",methods=["GET"])
def testApp():
    return "Running"

if __name__ == '__main__':
   app.run(debug = True,port=8007,host="0.0.0.0")