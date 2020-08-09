import re

class Recipe:
    
    """
    Constructor for this class
    """
    def __init__(self,recipe_id=None,recipe_name=None,meal_type=None,skill_level=None,servings=None,hours=None, 
                 minutes=None,meal_cat_id=None,ingredients=None,method=None,notes=None,image_URL=None):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.meal_type = meal_type
        self.skill_level = skill_level
        self.servings = servings
        self.hours = hours
        self.minutes = minutes
        self.meal_cat_id = meal_cat_id
        self.ingredients = ingredients
        self.method = method
        self.notes = notes
        self.image_URL = image_URL
        
    """
    Private function to convert ingredients, method and notes into the correct form.
    """
    def _fix_atts(self):
        #Converts the string into an array of strings
        if self.ingredients is None:
            self.ingredients = None
        else:
            self.ingredients = re.findall(r'\"(.+?)\"', self.ingredients)
        if self.method is None:
            self.method = None
        else:
            self.method = re.findall(r'\"(.+?)\"', self.method)
        if self.notes is None:
            self.notes = None
        else:
            self.notes = re.findall(r'\"(.+?)\"', self.notes)
        
    """
    Helper function for constructing recipes from a 2D array of rows
    """
    def construct_recipes(rows):
        list_of_recipes = []
        for row in rows:
            list_of_recipes.append(Recipe.construct_recipe(row))
        return list_of_recipes
        
    """
    Helper function to construct a recipe object from an array
    """
    def construct_recipe(row):
        new_recipe = Recipe()
        atts = [a for a in list(vars(new_recipe).keys()) if not a.startswith('__')]
        for x in range(len(atts)):
            setattr(new_recipe, atts[x],row[x]) 
        new_recipe._fix_atts()
        return new_recipe
        
    """
    String representation for this class.
    """
    def __str__(self):
        return str(vars(self))
        
    """
    Function to get the number of attributes stored in the recipe object (because it might change)
    """
    def get_num_atts():
        new_recipe = Recipe()
        atts = [a for a in list(vars(new_recipe).keys()) if not a.startswith('__')]
        return len(atts)