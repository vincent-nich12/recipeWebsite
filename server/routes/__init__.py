from flask import Blueprint
routes = Blueprint('routes', __name__)

from .viewers import *
from .searchers import *
from .manipulaters import *
from .authentication import *