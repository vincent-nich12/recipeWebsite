from flask import render_template, request
from . import routes
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.database_utils.SQLRunner import SQLRunner
from utils.searchers.RecipeSearcher import RecipeSearcher
from utils.common.general_utils import open_config_file
import traceback

"""
File for storing the routes involved with searching for things. It also contains Recipe_result that deals with clicking
on search results.
"""

config = open_config_file('/root/recipeWebsite/server/config.json')
databaseConnector = DatabaseConnector(config["database_config"]["access_file"])
sqlRunner = SQLRunner(databaseConnector)

#Handler for the recipe searcher in the header
@routes.route('/Recipe_Search_Header.html', methods=['GET'])
def headerSearcherHandler():
    searchType = request.args['searchSelect']
    searchValue = request.args['recipesearch']
    if searchType == "Title":
        recipes = searchRecipesByName(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))
    else:
        recipes = searchRecipesByIngredient(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))

#Search for a recipe by name
@routes.route('/Recipe_Search.html', methods=['GET'])
def searchName():
    try:
        #The value to search
        searchValue = request.args['recipesearch']
        recipes = searchRecipesByName(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes, num_recipes=len(recipes))
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html', emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()
        
#Search for a recipe by ingredients
@routes.route('/Ingredient_Search.html')
def searchIngredient():
    try:
        #The value to search
        searchValue = request.args['ingsearch']
        recipes = searchRecipesByIngredient(searchValue)
        return render_template('Recipe_Search.html',recipes=recipes,num_recipes=len(recipes))
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html', emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()
        
#Search by meal type (breakfast, lunch, dinner, dessert, snacks or other)
@routes.route('/Search_Meal_Type.html')
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
@routes.route('/Search_Category.html')
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
        
#Page displayed when you click on a recipe to view it
@routes.route('/Recipe_Result.html',methods=['GET'])
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
        return render_template('Recipe_Home.html', emsg='An unexpected error occured, please try again later.', error=e)
    finally:
        databaseConnector.close_connection()
        
############################################# Utils ##############################################
def searchRecipesByName(name):
    config = open_config_file('/root/recipeWebsite/server/config.json')
    #Connect to database
    databaseConnector.connect()
    #Get all the recipes and order by similarity
    #returned as a list of Recipe objects
    recipeSearcher = RecipeSearcher(sqlRunner,config["recipe_searcher"]["num_results"],config["recipe_searcher"]["similarity_threshold"])
    return recipeSearcher.search_recipes_by_name(name)
    
def searchRecipesByIngredient(ing):
    config = open_config_file('/root/recipeWebsite/server/config.json')
    #Connect to database
    databaseConnector.connect()
    #returned as a list of Recipe objects
    recipeSearcher = RecipeSearcher(sqlRunner,config["recipe_searcher"]["num_results"],config["recipe_searcher"]["similarity_threshold"])
    return recipeSearcher.search_recipes_by_ingredient(ing)
    
##################################################################################################