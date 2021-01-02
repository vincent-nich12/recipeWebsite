from flask import Flask

app = Flask(__name__)

# Declared results
import routes.viewers
import routes.searchers
import routes.manipulaters

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)