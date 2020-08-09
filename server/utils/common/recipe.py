

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
    Helper function for constructing recipes from a 2D array of rows
    """
    def construct_recipes(rows):
        list_of_recipes = []
        for row in rows:
            new_recipe = Recipe()
            atts = [a for a in list(vars(new_recipe).keys()) if not a.startswith('__')]
            for x in range(len(atts)):
                setattr(new_recipe, atts[x],row[x]) 
            list_of_recipes.append(new_recipe)
        return list_of_recipes