from flask import Flask, render_template
from flask import request

app = Flask(__name__)

#Homepage
@app.route('/')
def home():
	#open website
	return render_template('Recipe_Home.html')

#Add a recipe
@app.route('/Add_a_Recipe.html')
def addRecipes():
	return render_template('Add_a_Recipe.html')

#Search for a recipe by name
@app.route('/Recipe_Search.html')
def searchRecipe():
	return render_template('Recipe_Search.html')

#Search for a recipe by category
@app.route('/Category_Search.html')
def searchCategory():
	return render_template('Category_Search.html')

#Added Recipe Page
@app.route('/Added_Recipe.html')
def addedRecipe():
	return render_template('Added_Recipe.html')

#Favourites Page
@app.route('/Favourites.html')
def favs():
	return render_template('Favourites.html')

#Search for a recipe by ingredients
@app.route('/Ingredient_Search.html')
def ingredientSearch():
	return render_template('Ingredient_Search.html')

if __name__ == '__main__':
	app.run(debug=True, host="0.0.0.0")