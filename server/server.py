###################### External functions #######################

from flask import Flask, render_template, request, flash, redirect, url_for, abort
import psycopg2
import traceback
import os
from werkzeug.utils import secure_filename
import pickle
import re
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.searchers.RecipeSearcher import RecipeSearcher
from utils.database_utils.SQLRunner import SQLRunner
from utils.models.recipe import Recipe
from utils.models.categories import Categories
from utils.common.general_utils import upload_file, open_config_file

#################################################################

####################### Prerequisites ###########################
config = open_config_file('/root/recipeWebsite/server/config.json')
UPLOAD_FOLDER = config["misc"]["img_upload_folder"]
ALLOWED_EXTENSIONS = config["misc"]["allowed_extensions"]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

@app.before_request
def pre_server_setup():
    #Open the config file
    config = open_config_file('/root/recipeWebsite/server/config.json')
    #Check if connecting IP is valid
    if request.remote_addr not in config["misc"]["valid_ip_addresses"]:
        abort(403)

databaseConnector = DatabaseConnector(config["database_config"]["access_file"])
sqlRunner = SQLRunner(databaseConnector)
#################################################################

###################Functions to load webpages ###################
#Homepage
@app.route('/')
def home():
	#open website
    return render_template('Recipe_Home.html')

#Load the add a recipe page
@app.route('/Add_a_Recipe.html')
def addRecipe():
	return render_template('Add_a_Recipe.html')
    
 #Load the edit recipe page
@app.route('/Edit_Recipe.html')
def editRecipe():
	return render_template('Edit_Recipe.html')

 #Load the delete recipe page
@app.route('/Delete_Recipe.html')
def deleteRecipe():
	return render_template('Delete_Recipe.html')

#Load the login page
@app.route('/Login_Page.html')
def loginPage():
	return render_template('Login_Page.html')


#Search for a recipe by name
@app.route('/Recipe_Search.html', methods=['GET'])
def searchRecipe():
    try:
        #The value to search
        searchValue = request.args['recipesearch']
        #Connect to database
        databaseConnector.connect()
        #Get all the recipes and order by similarity
        #returned as a list of Recipe objects
        recipeSearcher = RecipeSearcher(sqlRunner,config["recipe_searcher"]["num_results"],config["recipe_searcher"]["similarity_threshold"])
        recipes = recipeSearcher.search_recipes_by_name(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html',emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()

#Search for a recipe by category
@app.route('/Category_Search.html')
def searchCategory():
	return render_template('Category_Search.html')

#Page Rendered when a recipe is sent for previewing
@app.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        #Create a Recipes object
        recipe = Recipe.create_recipe_object_from_website(request,databaseConnector)
        #Image upload handler
        file_URL = upload_file(app,request,recipe.recipe_id,ALLOWED_EXTENSIONS)
        recipe.image_URL = file_URL
        #Create the categories object
        categories = Categories.create_categories_object_from_website(request,recipe.recipe_id)
        #Save the details temporarly into a pickle file
        with open('newItems.pkl', 'wb') as f:
            pickle.dump([recipe,categories],f)
        return render_template('Preview_Recipe.html',recipe=recipe,categories=categories.get_categories_as_list())
    except Exception as e:
        #print(e)
        #This shouldn't occur but just incase...
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()

#Function called by the preview page to submit the recipes 
@app.route('/Submitted_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        databaseConnector.connect()
        #load saved variables
        file = open('newItems.pkl','rb')
        data = pickle.load(file)
        file.close()
        recipe = data[0]
        categories = data[1]
        #Submit data to the database
        categories.submit_categories_to_database(sqlRunner)
        recipe.submit_recipe_to_database(sqlRunner)  
        return render_template('Submitted_Recipe.html',error=None,recipe=recipe,categories=categories.get_categories_as_list())
    except Exception as e:
        traceback.print_exc()
        return render_template('Submitted_Recipe.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()

#Favourites Page
@app.route('/Favourites.html')
def favs():
	return render_template('Favourites.html')

#Search for a recipe by ingredients
@app.route('/Ingredient_Search.html')
def ingredientSearch():
    #The value to search
    searchValue = request.args['ingsearch']
    #Connect to database
    databaseConnector.connect()
    #Get all the recipes and order by similarity
    #returned as a list of Recipe objects
    recipeSearcher = RecipeSearcher(sqlRunner,config["recipe_searcher"]["num_results"],config["recipe_searcher"]["similarity_threshold"])
    recipes = recipeSearcher.search_recipes_by_ingredient(searchValue)
    return render_template('Ingredient_Search.html',recipes=recipes,num_recipes=len(recipes))
    
#Recipe Search Result
@app.route('/Recipe_Result.html',methods=['GET'])
def recipeResult():
    try:
        #get the recipe name
        recipeName = request.args.get('recipeName')
        databaseConnector.connect()
        recipeAtts = sqlRunner.run_script('SELECT * FROM recipes INNER JOIN meal_cats ON \
                                           recipes.meal_cat_id = meal_cats.meal_cat_id WHERE \
                                           recipes.recipe_name = %s', [recipeName])
        recipeAtts = recipeAtts[0]
        # Construct the recipe object
        recipe = Recipe.construct_recipe(recipeAtts,True)
        # Remove the recipe atts and only use the category atts 
        recipeAtts = recipeAtts[Recipe.get_num_atts():len(recipeAtts)]
        # Construct the categories object
        categories = Categories.construct_categories_for_recipe(recipeAtts)
        return render_template('Recipe_Result.html',recipe=recipe,categories=categories.get_categories_as_list())
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
	
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")