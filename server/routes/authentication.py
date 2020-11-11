from flask import render_template, request, abort, redirect
from . import routes
from utils.common.general_utils import open_config_file

config = open_config_file('/root/recipeWebsite/server/config.json')

@routes.before_request
def pre_server_setup():
    #Open the config file
    config = open_config_file('/root/recipeWebsite/server/config.json')
    #Check if connecting IP is valid
    if request.remote_addr not in config["misc"]["valid_ip_addresses"]:
        abort(403)
    #redirect if connecting via HTTP not HTTPS
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)