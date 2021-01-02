# Necessary import
from __main__ import app
from flask import render_template
from utils.common.general_utils import open_config_file

config = open_config_file('/root/recipeWebsite/server/config.json')

"""
File for storing the routes that deal with viewing pages only (not search results)
"""

#Load the homepage
@app.route('/')
def home():
	#open website
    return render_template('Recipe_Home.html')
	
#Load the delete recipe page (not currently functional)
@app.route('/Delete_Recipe.html')
def deleteRecipe():
	return render_template('Delete_Recipe.html')

#Load the login page
@app.route('/Login_Page.html')
def loginPage():
	return render_template('Login_Page.html')
	
#Load the search by categories page
@app.route('/Category_Search.html')
def categorySearch():
    config = open_config_file('/root/recipeWebsite/server/config.json')
    categories = sorted(config["misc"]["categories"])
    return render_template('Category_Search.html', categoryNames = categories)
	
#Load the Favourites Page (not currently functional)
@app.route('/Favourites.html')
def favs():
	return render_template('Favourites.html')