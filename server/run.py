from flask import Flask
from routes import *
import os
import gevent
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.register_blueprint(routes)

privKey = '../../../../etc/letsencrypt/live/nkrecipes.co.uk/privkey.pem'
certFile = '../../../../etc/letsencrypt/live/nkrecipes.co.uk/fullchain.pem'

# Run it within native Flask (just port 443) or gevent (both port 443 and 80 but no stdout)
debugMode = False


if __name__ == '__main__':
    if debugMode:
        app.run(debug=True, host="0.0.0.0", port=443, ssl_context=('../../../../etc/letsencrypt/live/nkrecipes.co.uk/fullchain.pem',
        '../../../../etc/letsencrypt/live/nkrecipes.co.uk/privkey.pem'))
    else:
        https_server = WSGIServer(('0.0.0.0', 443), app, keyfile=privKey, certfile=certFile)
        https_server.start()

        http_server = WSGIServer(('0.0.0.0', 80), app)
        http_server.start()

        while True:
            gevent.sleep(60)