# Necessary import
from __main__ import app
from flask import render_template, request
import traceback
from utils.common.general_utils import open_config_file, upload_recipe_image, copy_temp_img_file
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.database_utils.SQLRunner import SQLRunner
from utils.web_scrapers.WebScraper import WebScraper
from utils.models.recipe import Recipe
from utils.common.search_utils import searchRecipesByName
import pickle
from random import random
from utils.searchers.RecipeSearcher import RecipeSearcher

"""
File for storing the routes used to manipulate recipes e.g. adding, editing and deleting recipes.
"""
config = open_config_file('config.json')
databaseConnector = DatabaseConnector(config["database_config"]["access_file"])
sqlRunner = SQLRunner(databaseConnector)


#################################################### Add a recipe ########################################################
# Load the add a recipe page (1st stage for adding a recipe)
@app.route('/Add_a_Recipe.html')
def addRecipe():
    col1, col2, col3 = createCategoryColumns()
    return render_template('Add_a_Recipe.html', recipe=None, col1=col1, col2=col2, col3=col3)


# Page Rendered when a recipe is sent for previewing (2nd stage for adding a new recipe)
@app.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        config = open_config_file('config.json')
        # Create a Recipes object using the request, databaseConnector object and the valid category names
        recipe = Recipe.create_recipe_object_from_website(request, databaseConnector, config["misc"]["categories"])
        # Image upload handler (to a temporary location for previewing)
        recipe.image_URL = upload_recipe_image(config, request)
        # Get the selected categories
        categories = recipe.get_categories(config["misc"]["categories"])
        # Save the details temporarly into a pickle file
        with open('newItems.pkl', 'wb') as f:
            pickle.dump([recipe, categories], f)
        return render_template('Preview_Recipe.html', recipe=recipe, categories=categories, rnd=random())
    except Exception as e:
        # print(e)
        # This shouldn't occur but just incase...
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()


# Function called by the preview page to submit the recipes (final stage)
@app.route('/Submitted_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        config = open_config_file('config.json')
        databaseConnector.connect()
        # load saved variables
        file = open('newItems.pkl', 'rb')
        data = pickle.load(file)
        file.close()
        recipe = data[0]
        categories = data[1]
        # Upload image to the server
        recipe.image_URL = copy_temp_img_file(config, recipe)
        # Submit data to the database
        recipe.submit_recipe_to_database(sqlRunner)
        return render_template('Submitted_Recipe.html', error=None, recipe=recipe, categories=categories)
    except Exception as e:
        traceback.print_exc()
        return render_template('Submitted_Recipe.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()


# Function called to fill in the recipe details given by a URL
@app.route('/Get_Recipe_From_URL.html', methods=['GET'])
def getRecipeFromURL():
    col1, col2, col3 = createCategoryColumns()
    try:
        url = request.args.get("recipe_URL")
        web_scraper = WebScraper()
        recipe = web_scraper.get_recipe_from_url(url)

        return render_template('Add_a_Recipe.html', recipe=recipe, col1=col1, col2=col2, col3=col3)
    except:
        config = open_config_file('config.json')
        return render_template('Add_a_Recipe.html', recipe=None, error="An unknown error has occured",
                               categoryNames=config["misc"]["categories"], col1=col1, col2=col2, col3=col3)


def createCategoryColumns():
    config = open_config_file('config.json')
    catNames = sorted(config["misc"]["categories"])
    # Split the catNames into 3 columns (as this is how they are displayed
    col1 = []
    for x in range(0, len(catNames), 3):
        col1.append(catNames[x])
    col2 = []
    for x in range(1, len(catNames), 3):
        col2.append(catNames[x])
    col3 = []
    for x in range(2, len(catNames), 3):
        col3.append(catNames[x])

    return col1, col2, col3


##########################################################################################################################

################################################## Edit a Recipe #########################################################
# Load the edit recipe page
@app.route('/Edit_Recipe.html', methods=['GET'])
def editRecipe():
    try:
        config = open_config_file('config.json')
        name = request.args.get("recipeName")
        recipe = searchRecipesByName(name)[0]
        categories = recipe.get_categories(config["misc"]["categories"])
        col1, col2, col3 = createCategoryColumns()
        return render_template('Edit_Recipe.html', recipe=recipe, categories=categories, col1=col1, col2=col2,
                               col3=col3)
    except:
        traceback.print_exc()
        return render_template('Recipe_Home.html')


# Submit the updates changes to a recipe
@app.route('/Edit_Recipe_Submit.html', methods=['POST'])
def submitEdittedRecipe():
    try:
        config = open_config_file('config.json')
        # Create a Recipes object using the request, databaseConnector object and the valid category names
        recipe = Recipe.create_recipe_object_from_website(request, databaseConnector, config["misc"]["categories"])
        # Get its ID
        recipe.recipe_id = request.form['recipe_id']
        # Image handle:
        # Get the original recipe object
        rs = RecipeSearcher(sqlRunner)
        original_recipe_object = rs.search_recipes_by_name(recipe.recipe_name)[0]
        # check if a new image has been added
        imageURL = upload_recipe_image(config, request)
        new_image_uploaded = imageURL is not None
        # If no image uploaded, do nothing
        if not new_image_uploaded:
            recipe.image_URL = original_recipe_object.image_URL
        else:
            # If there is a new image, upload it
            recipe.image_URL = imageURL
            recipe.image_URL = copy_temp_img_file(config, recipe)
        # Submit the updated details to the database
        recipe.submit_recipe_to_database(sqlRunner, isEdit=True)
        # Get the categories from the Recipe object
        categories = recipe.get_categories(config["misc"]["categories"])
        return render_template('Recipe_Result.html', recipe=recipe, categories=categories, rnd=random())
    except Exception as e:
        # This shouldn't occur but just incase...
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()


########################################################################################################################

################################################## Delete a Recipe #####################################################
# Load the delete recipe page (asks if the user is sure they want to delete the recipe)
@app.route('/Delete_Recipe.html')
def delete_recipe():
    try:
        recipe_name = request.args.get('recipeName')
        return render_template('Delete_Recipe.html', recipeName=recipe_name)
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html')


# Function to handle when a recipe is confirmed for deletion or not
@app.route('/Delete_Recipe_Submit.html', methods=['POST'])
def delete_recipe_submit():
    recipe_for_deletion = request.form['recipeName']
    # See what button the user selected
    try:
        button_selected = request.form['Yes']
    except Exception as e:
        button_selected = "No"
    try:
        databaseConnector.connect()
        sql_runner = SQLRunner(databaseConnector)
        rs = RecipeSearcher(sql_runner=sql_runner)
        recipe = rs.search_recipes_by_name(recipe_for_deletion)[0]
        # If button selected was no, then go back to the original page
        if button_selected == "No":
            return render_template('Recipe_Result.html', recipe=recipe)
        # If yes, then delete the recipe
        sql_runner.run_script("DELETE FROM Recipes WHERE recipe_id=%s", values=[recipe.recipe_id])
        return render_template('Delete_Recipe_Final.html')
    except Exception as e:
        traceback.print_exc()
        return render_template('Delete_Recipe_Final.html', error=e)
    finally:
        databaseConnector.close_connection()
########################################################################################################################
