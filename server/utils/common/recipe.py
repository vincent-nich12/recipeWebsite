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
    Helper function for constructing recipes from a 2D array of rows (recipes)
    """
    def construct_recipes(rows,isFromDatabase):
        list_of_recipes = []
        for row in rows:
            list_of_recipes.append(Recipe.construct_recipe(row,isFromDatabase))
        return list_of_recipes
        
    """
    Helper function to construct a recipe object from an array
    The array needs to be the following:
        1) recipe_ID - int
        2) recipe_name - string
        3) meal_type (Breakfast,Lunch,Dinner,Dessert, Snacks or Other) - int
        4) skill_level (Easy, Medium or Hard) - string
        5) servings
        6) hours
        7) minutes
        8) the id of the category
        9) ingredients
        10) method
        11) notes
        12) URL to the image
    """
    def construct_recipe(row,isFromDatabase):
        new_recipe = Recipe()
        atts = [a for a in list(vars(new_recipe).keys()) if not a.startswith('__')]
        for x in range(len(atts)):
            setattr(new_recipe, atts[x],row[x]) 
        if isFromDatabase:
            new_recipe._fix_atts()
        return new_recipe
        
    """
    String representation for this class.
    """
    def __str__(self):
        return str(vars(self))
        
    """
    Function to extract the new desired ID for a recipe. It
    requires the databaseConnector object in order to do this.
    """
    def get_ID_for_new_recipe(databaseConnector):
        databaseConnector.cur.execute('SELECT * FROM recipes')
        rows = databaseConnector.cur.fetchall()
		
        numRecords = 0
        numRecords = len(rows)
            
        newID = numRecords + 1
        
        return newID
        
    """
    Function inorder to extract the information required from a website
    to create a new Recipe object.
    Requires the request and databaseConnector objects. It does not take 
    in the Image Information, this needs to be added later to the object
    if required.
    """
    def create_recipe_object_from_website(request,databaseConnector):
        #connect to database
        databaseConnector.connect()

        ##########################################################
        #Gather the information required for a recipe
        recipeArray = []
        newID = Recipe.get_ID_for_new_recipe(databaseConnector)
        #Get the assigned ID for the new recipe to be added.
        recipeArray.append(newID)
        #Recipe title
        recipeArray.append(request.form['recipe_name'])
        #Breakfast, Lunch, Dinner, Dessert, Snacks or Other
        recipeArray.append(request.form['meal'])
        #Easy, Medium or Hard
        recipeArray.append(request.form['skill_level'])
        #Number of servings
        recipeArray.append(request.form['servings'])
        #Time taken to complete the recipe
        recipeArray.append(request.form['hours'])
        recipeArray.append(request.form['minutes'])
        #Category ID (same as Recipe ID)
        recipeArray.append(newID)
        ############## Add Ingredients ####################
        #Ingredients textbox 
        ingredients = request.form['ingredients']
        #Split by new line.
        ingredients = ingredients.split('\n')
        recipeArray.append(ingredients)
        ##################################################
        
        ############## Add Method ########################
        #Method textbox
        method = request.form['Method']
        #Split by new line.
        method = method.split('\n')
        recipeArray.append(method)
        ##################################################
        #Notes textbox
        recipeArray.append(request.form['notes'])
        #Add None for Image_URL
        recipeArray.append("")
        # Create the recipe object
        recipe = Recipe.construct_recipe(recipeArray,False)
        
        return recipe
        
    """
    Function to get the number of attributes stored in the recipe object (because it might change)
    """
    def get_num_atts():
        new_recipe = Recipe()
        atts = [a for a in list(vars(new_recipe).keys()) if not a.startswith('__')]
        return len(atts)
        
    