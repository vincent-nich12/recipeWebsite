from flask import render_template, request, abort, Flask, redirect
from utils.common.general_utils import open_config_file

config = open_config_file('/root/recipeWebsite/server/config.json')
app = Flask(__name__)

@app.before_request
def pre_server_setup():
    #Open the config file
    config = open_config_file('/root/recipeWebsite/server/config.json')
    #Check if connecting IP is valid
    if request.remote_addr not in config["misc"]["valid_ip_addresses"]:
        abort(403)
        
    #Redirect from http to https
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0", port=80)
