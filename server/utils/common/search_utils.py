from utils.common.general_utils import open_config_file
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.database_utils.SQLRunner import SQLRunner
from utils.searchers.RecipeSearcher import RecipeSearcher

"""
File used for storing the methods that deal with searching recipes.
"""

config = open_config_file('/root/recipeWebsite/server/config.json')
databaseConnector = DatabaseConnector(config["database_config"]["access_file"])
sqlRunner = SQLRunner(databaseConnector)

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