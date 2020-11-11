from flask import Flask
from routes import *
import os
import gevent
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.register_blueprint(routes)

privKey = '../../../../etc/letsencrypt/live/nkrecipes.co.uk/privkey.pem'
certFile = '../../../../etc/letsencrypt/live/nkrecipes.co.uk/fullchain.pem'


if __name__ == '__main__':
    https_server = WSGIServer(('0.0.0.0', 443), app, keyfile=privKey, certfile=certFile)
    https_server.start()

    http_server = WSGIServer(('0.0.0.0', 80), app)
    http_server.start()

    while True:
        gevent.sleep(60)