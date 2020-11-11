from flask import render_template, request
from . import routes
import traceback
from utils.common.general_utils import open_config_file, upload_recipe_image,copy_temp_img_file
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.database_utils.SQLRunner import SQLRunner
from utils.web_scrapers.WebScraper import WebScraper
from utils.models.recipe import Recipe
from utils.common.search_utils import searchRecipesByName
import re
from werkzeug.utils import secure_filename
import pickle
import os
from random import random

"""
File for storing the routes used to manipulate recipes e.g. adding, editing and deleting recipes.
"""

config = open_config_file('/root/recipeWebsite/server/config.json')
databaseConnector = DatabaseConnector(config["database_config"]["access_file"])
sqlRunner = SQLRunner(databaseConnector)

#################################################### Add a recipe ########################################################
#Load the add a recipe page (1st stage for adding a recipe)
@routes.route('/Add_a_Recipe.html')
def addRecipe():
    col1,col2,col3 = createCategoryColumns()
    return render_template('Add_a_Recipe.html', recipe=None, col1=col1, col2=col2, col3=col3)

#Page Rendered when a recipe is sent for previewing (2nd stage for adding a new recipe)
@routes.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        #Create a Recipes object using the request, databaseConnector object and the valid category names
        recipe = Recipe.create_recipe_object_from_website(request,databaseConnector,config["misc"]["categories"])
        #Image upload handler (to a temporary location for previewing)
        recipe.image_URL = upload_recipe_image(config,request)
        #Get the selected categories
        categories = recipe.get_categories(config["misc"]["categories"])
        #Save the details temporarly into a pickle file
        with open('/root/recipeWebsite/server/newItems.pkl', 'wb') as f:
            pickle.dump([recipe,categories],f)
        return render_template('Preview_Recipe.html',recipe=recipe,categories=categories, rnd=random())
    except Exception as e:
        #print(e)
        #This shouldn't occur but just incase...
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
        
#Function called by the preview page to submit the recipes (final stage)
@routes.route('/Submitted_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        databaseConnector.connect()
        #load saved variables
        file = open('/root/recipeWebsite/server/newItems.pkl','rb')
        data = pickle.load(file)
        file.close()
        recipe = data[0]
        categories = data[1]
        #Upload image to the server
        recipe.image_URL = copy_temp_img_file(config,recipe)
        #Submit data to the database
        recipe.submit_recipe_to_database(sqlRunner)  
        return render_template('Submitted_Recipe.html',error=None,recipe=recipe,categories=categories)
    except Exception as e:
        traceback.print_exc()
        return render_template('Submitted_Recipe.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
        
#Function called to fill in the recipe details given by a URL    
@routes.route('/Get_Recipe_From_URL.html', methods=['GET'])
def getRecipeFromURL():
    col1, col2, col3 = createCategoryColumns()
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        url = request.args.get("recipe_URL")
        web_scraper = WebScraper()
        recipe = web_scraper.get_recipe_from_url(url)
        
        return render_template('Add_a_Recipe.html', recipe=recipe, col1=col1, col2=col2, col3=col3)
    except:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        return render_template('Add_a_Recipe.html', recipe=None, error="An unknown error has occured", categoryNames = config["misc"]["categories"], col1=col1, col2=col2, col3=col3)
        
def createCategoryColumns():
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
        
    return col1,col2,col3
    
##########################################################################################################################

################################################## Edit a Recipe #########################################################
#Load the edit recipe page (not currently functional)
@routes.route('/Edit_Recipe.html', methods=['GET'])
def editRecipe():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        name = request.args.get("recipeName")
        recipe = searchRecipesByName(name)[0]
        categories = recipe.get_categories(config["misc"]["categories"])
        col1,col2,col3 = createCategoryColumns()
        return render_template('Edit_Recipe.html', recipe=recipe, categories=categories, col1=col1, col2=col2, col3=col3)
    except:
        traceback.print_exc()
        return render_template('Recipe_Home.html')

@routes.route('/Edit_Recipe_Submit.html', methods=['POST'])
def submitEdittedRecipe():
    try:
        config = open_config_file('/root/recipeWebsite/server/config.json')
        #Create a Recipes object using the request, databaseConnector object and the valid category names
        recipe = Recipe.create_recipe_object_from_website(request,databaseConnector,config["misc"]["categories"])
        
        return str(recipe)
        
        
        
        #Image upload handler (to a temporary location for previewing)
        recipe.image_URL = upload_recipe_image(config,request)
        #Get the selected categories
        categories = recipe.get_categories(config["misc"]["categories"])
        #Save the details temporarly into a pickle file
        with open('/root/recipeWebsite/server/newItems.pkl', 'wb') as f:
            pickle.dump([recipe,categories],f)
        return render_template('Preview_Recipe.html',recipe=recipe,categories=categories, rnd=random())
    except Exception as e:
        #This shouldn't occur but just incase...
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
    #return "changes submitted successfully"

##########################################################################################################################















