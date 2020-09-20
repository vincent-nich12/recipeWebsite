from utils.models.recipe import Recipe

"""
This class is for searching recipes in the database.
"""
class RecipeSearcher:
    
    """
    Create the object
    """
    def __init__(self,sql_runner, num_results = 10, similarity_score = 0.2):
        self.sql_runner = sql_runner
        self.num_results = num_results
        self.similarity_score = similarity_score
       
    """
    Function to get all the recipes by name.
    Returned as a list of Recipe objects.
    """
    def search_recipes_by_name(self, search_value):
        #Get all the recipes and order by similarity
        rows = self.sql_runner.run_script("SELECT * FROM Recipes WHERE similarity(Recipe_Name,'" + search_value.lower() + "') > " + str(self.similarity_score) + " ORDER BY \
                                           similarity(lower(Recipe_Name),'" + search_value \
                                           + "') DESC;",[])
        #Get the top self.num_results results
        topRecipes = None
        if len(rows) < self.num_results:
            topRecipes = rows
        else:
            topRecipes = rows[0:self.num_results]
        #Convert into a list of Recipe objects
        recipes = Recipe.construct_recipes(topRecipes,True)
        return recipes
        
    """
    Function to get all the recipes that contain a particular ingredient.
    Recturn as a list of Recipe objects.
    """
    def search_recipes_by_ingredient(self, search_value):
        #Get all the recipes that contain a particular ingredient
        rows = self.sql_runner.run_script("SELECT * FROM Recipes WHERE position('" + search_value.lower() + "' in lower(ingredients))>0", [])
        #Get the top self.num_results results
        topRecipes = None
        if len(rows) < self.num_results:
            topRecipes = rows
        else:
            topRecipes = rows[0:self.num_results]
        #Convert into a list of Recipe objects
        recipes = Recipe.construct_recipes(topRecipes,True)
        return recipes
        