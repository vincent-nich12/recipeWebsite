from flask import Flask
from routes import *
import os

app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=443, ssl_context=('../../../../etc/letsencrypt/live/nkrecipes.co.uk/fullchain.pem',
    '../../../../etc/letsencrypt/live/nkrecipes.co.uk/privkey.pem'))