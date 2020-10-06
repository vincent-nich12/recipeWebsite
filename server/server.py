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
from utils.common.general_utils import upload_file, open_config_file
from utils.web_scrapers.WebScraper import WebScraper

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
    config = open_config_file('/root/recipeWebsite/server/config.json')
    catNames = sorted(config["misc"]["categories"])
    #Split the catNames into 3 columns (as this is how they are displayed
    col1 = []
    for x in range(0,len(catNames),3):
        col1.append(catNames[x])
    col2 = []
    for x in range(1,len(catNames),3):
        col2.append(catNames[x])
    col3 = []
    for x in range(2,len(catNames),3):
        col3.append(catNames[x])
    return render_template('Add_a_Recipe.html', recipe=None, col1=col1, col2=col2, col3=col3)
    
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

#Function to get up the search by category page
@app.route('/Category_Search.html')
def categorySearch():
    config = open_config_file('/root/recipeWebsite/server/config.json')
    categories = sorted(config["misc"]["categories"])
    return render_template('Category_Search.html', categoryNames = categories)

#Page Rendered when a recipe is sent for previewing
@app.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        #Create a Recipes object using the request, databaseConnector object and the valid category names
        recipe = Recipe.create_recipe_object_from_website(request,databaseConnector,config["misc"]["categories"])
        #Image upload handler
        file_URL = upload_file(app,request,recipe.recipe_id,ALLOWED_EXTENSIONS)
        recipe.image_URL = file_URL
        #Get the selected categories
        categories = recipe.get_categories(config["misc"]["categories"])
        #Save the details temporarly into a pickle file
        with open('/root/recipeWebsite/server/newItems.pkl', 'wb') as f:
            pickle.dump([recipe,categories],f)
        return render_template('Preview_Recipe.html',recipe=recipe,categories=categories)
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
        file = open('/root/recipeWebsite/server/newItems.pkl','rb')
        data = pickle.load(file)
        file.close()
        recipe = data[0]
        categories = data[1]
        #Submit data to the database
        recipe.submit_recipe_to_database(sqlRunner)  
        return render_template('Submitted_Recipe.html',error=None,recipe=recipe,categories=categories)
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
    return render_template('Recipe_Search.html',recipes=recipes,num_recipes=len(recipes))
    
#Page displayed when you click on a recipe to view it
@app.route('/Recipe_Result.html',methods=['GET'])
def recipeResult():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        #The value to search
        searchValue = request.args.get('recipeName')
        #Connect to database
        databaseConnector.connect()
        #Get the recipe with that name
        recipeSearcher = RecipeSearcher(sqlRunner,config["recipe_searcher"]["num_results"],config["recipe_searcher"]["similarity_threshold"])
        recipes = recipeSearcher.search_recipes_by_name(searchValue)
        #Just extract the first one
        recipe = recipes[0]
        #Get the categories from the Recipe object
        categories = recipe.get_categories(config["misc"]["categories"])
        return render_template('Recipe_Result.html',recipe=recipe,categories=categories)
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
        
#Function called when user wants to search by meal type (i.e. breakfast,lunch,dinner etc.)
@app.route('/Search_Meal_Type.html')
def searchMealType():
    try:
        #The value to search
        searchValue = request.args.get('type')
        #Connect to database
        databaseConnector.connect()
        #Get all the recipes that fall under a particular type (-1 to display ALL results)
        recipeSearcher = RecipeSearcher(sqlRunner,-1)
        recipes = recipeSearcher.get_recipes_by_type(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html',emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()
    
#Function called when user wants to search by category
@app.route('/Search_Category.html')
def searchCategory():
    try:
        #The value to search
        searchValue = request.args.get('type')
        #Connect to database
        databaseConnector.connect()
        #Get all the recipes that fall under a particular type (-1 to display ALL results)
        recipeSearcher = RecipeSearcher(sqlRunner,-1)
        recipes = recipeSearcher.get_recipes_by_category(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html',emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()
        
@app.route('/Get_Recipe_From_URL.html', methods=['GET'])
def getRecipeFromURL():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        url = request.args.get("recipe_URL")
        web_scraper = WebScraper()
        recipe = web_scraper.get_recipe_from_url(url)
        return render_template('Add_a_Recipe.html', recipe=recipe, categoryNames = config["misc"]["categories"])
    except:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        return render_template('Add_a_Recipe.html', recipe=None, error="An unknown error has occured", categoryNames = config["misc"]["categories"])
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")