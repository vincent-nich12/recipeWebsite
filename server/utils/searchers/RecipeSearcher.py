from utils.common.recipe import Recipe

"""
This class is for searching recipes in the database.
"""
class RecipeSearcher:
    
    """
    Create the object
    """
    def __init__(self,sql_runner,search_value,num_results):
        self.sql_runner = sql_runner
        self.search_value = search_value
        self.num_results = num_results
       
    """
    Function to get all the recipes from the search value.
    Returned as a list of Recipe objects.
    """
    def search_recipes(self):
        #Get all the recipes and order by similarity
        rows = self.sql_runner.run_script("SELECT * FROM Recipes ORDER BY \
                                           similarity(Recipe_Name,'" + self.search_value \
                                           + "') DESC;",[])
        #Get the top self.search_recipes results
        topRecipes = None
        if len(rows) < self.num_results:
            topRecipes = rows
        else:
            topRecipes = rows[0:self.num_results]
        #Convert into a list of Recipe objects
        recipes = Recipe.construct_recipes(topRecipes,True)
        return recipes
        