import re
from utils.database_utils.DatabaseConnector import DatabaseConnector

class Recipe:
    
    """
    Constructor for this class
    """
    def __init__(self,recipe_id=None,recipe_name=None,meal_type=None,skill_level=None,servings=None,hours=None, 
                 minutes=None,ingredients=None,method=None,notes=None,image_URL=None,categories=None):
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.meal_type = meal_type
        self.skill_level = skill_level
        self.servings = servings
        self.hours = hours
        self.minutes = minutes
        self.ingredients = ingredients
        self.method = method
        self.notes = notes
        self.image_URL = image_URL
        self.categories = categories
        
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
        if self.categories is None:
            self.categories = None
        else:
            self.categories = self.categories.replace('"', '').strip('}{').split(',')
        
    """
    String representation for this class.
    """
    def __str__(self):
        return str(vars(self))

    """
    Function to get the categories of the recipe.
    Since the array stored in the database may contain categories that are not 
    given in the config.json file, this function filters these out.
    """
    def get_categories(self, categoryNames):
        categoriesStored = self.categories
        categories = []
        for cats in categoriesStored:
            # Ensure that the string search is case insensitive
            if cats.lower() in (catNames.lower() for catNames in categoryNames):
                categories.append(cats)
        return categories

    """
    Function used to submit a recipe object into the database
    """
    def submit_recipe_to_database(self, sqlRunner, isEdit=False):
        sqlString = None
        if isEdit:
            sqlString = self._create_edit_string()
            sqlRunner.run_script(sqlString, [])
        else:
            sqlString = self._create_insert_string()
            values = self._get_values()
            sqlRunner.run_script(sqlString, values)

    """
    Method for creating the insert string for a recipe object
    """
    def _create_insert_string(self):
        sqlString = "INSERT INTO recipes VALUES ("
        for x in range(Recipe.get_num_atts()):
            if x < Recipe.get_num_atts() - 1:
                sqlString = sqlString + "%s,"
            else:
                sqlString = sqlString + "%s)"
        return sqlString

    """
    Method for creating the edit string for a recipe object
    """
    def _create_edit_string(self):
        sqlString = "UPDATE recipes SET "
        names = self._get_names()
        vals = self._get_values()
        for x in range(1, Recipe.get_num_atts()):
            valToAdd = str(vals[x])
            # Convert lists to sets
            if type(vals[x]) is list:
                valToAdd = str(set(vals[x]))
            if names[x] == "image_URL":
                if len(str(vals[x])) == 0:
                    continue
            # replace single quotes with double quotes
            valToAdd = valToAdd.replace("'", "\"")
            if x < Recipe.get_num_atts() - 1:
                sqlString = sqlString + names[x] + "=" + "'" + valToAdd + "'" + ", "
            else:
                sqlString = sqlString + names[x] + "=" + "'" + valToAdd + "'"
        sqlString = sqlString + " WHERE recipe_id = " + str(self.recipe_id) + ";"
        return sqlString

    """
    Function to get all the field values stored in the Recipe object into a list.
    """
    def _get_values(self):
        atts = self._get_names()
        attVals = []
        for x in range(len(atts)):
            attVals.append(getattr(self, atts[x]))
        return attVals

    """
    Function to get all field names stored in the Recipe object as a list.
    """
    def _get_names(self):
        return [a for a in list(vars(self).keys()) if not a.startswith('__')]

    """
    Function to display a recipe's ingredients as a string (for the HTML).
    """
    def ingredients_str(self):
        strRep = ''
        for ing in self.ingredients:
            strRep = strRep + ing + "\n"
        return strRep

    """
    Function to display a recipe's method as a string (for the HTML).
    """
    def method_str(self):
        strRep = ''
        for line in self.method:
            strRep = strRep + line + "\n"
        return strRep

    """
    Function to display a recipe's notes as a string (for the HTML).
    """
    def notes_str(self):
        strRep = ''
        for line in self.notes:
            strRep = strRep + line + "\n"
        return strRep

    """
    Function to get the number of attributes stored in the recipe object (because it might change)
    """
    @staticmethod
    def get_num_atts():
        new_recipe = Recipe()
        atts = new_recipe._get_names()
        return len(atts)

    """
    Helper function to construct a recipe object from an array
    The array needs to match the order of attributes stored in the database.
    """
    @staticmethod
    def construct_recipe(row, is_from_database:bool):
        new_recipe = Recipe()
        atts = new_recipe._get_names()
        for x in range(len(atts)):
            if row[x] == 'None':
                setattr(new_recipe, atts[x], None)
            else:
                setattr(new_recipe, atts[x], row[x])
        if is_from_database:
            new_recipe._fix_atts()
        return new_recipe

    """
    Function to extract the new desired ID for a recipe. It
    requires the databaseConnector object in order to do this.
    """
    @staticmethod
    def get_ID_for_new_recipe(database_conn: DatabaseConnector):
        database_conn.cur.execute('SELECT recipe_id FROM recipes')
        rows = database_conn.cur.fetchall()
        rowIDs = []
        for row in rows:
            rowIDs.append(row[0])
        return max(rowIDs) + 1

    """
    Helper function for constructing recipes from a 2D array of rows (recipes)
    """
    @staticmethod
    def construct_recipes(rows, is_from_database:bool):
        list_of_recipes = []
        for row in rows:
            list_of_recipes.append(Recipe.construct_recipe(row, is_from_database))
        return list_of_recipes

    """
    Function inorder to extract the information required from a website
    to create a new Recipe object.
    Requires the request and databaseConnector objects. It does not take 
    in the Image Information, this needs to be added later to the object
    if required.
    """
    @staticmethod
    def create_recipe_object_from_website(request,database_conn, cat_names):
        #connect to database
        database_conn.connect()
        ##########################################################
        #Gather the information required for a recipe
        recipeArray = []
        newID = Recipe.get_ID_for_new_recipe(database_conn)
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
        ############## Add Ingredients ####################
        #Ingredients textbox
        ingredients = request.form['ingredients']
        #Split by new line.
        ingredients = ingredients.split('\n')
        # Get rid off hidden chars
        recipeArray.append(clean_text(ingredients))
        ##################################################

        ############## Add Method ########################
        #Method textbox
        method = request.form['Method']
        #Split by new line.
        method = method.split('\n')
        # Get rid off hidden chars
        recipeArray.append(clean_text(method))
        ##################################################

        ############# Add Notes ##########################
        #Notes textbox
        notes = request.form['notes']
        #Split by new line.
        notes = notes.split('\n')
        # Get rid off hidden chars
        recipeArray.append(clean_text(notes))
        ##################################################
        #Add Empty string for Image_URL
        recipeArray.append("")
        ############# Get Categories #####################
        catsArray = []
        for catName in cat_names:
            if request.form.get(catName) is None:
                pass
            else:
                catsArray.append(request.form.get(catName))
        recipeArray.append(catsArray)
        ##################################################
        # Create the recipe object
        recipe = Recipe.construct_recipe(recipeArray,False)
        return recipe


# Helper function for cleaning out white spaces in textboxes
def clean_text(text_arr:list):
    text_arr = [x.replace("\r", "") for x in text_arr]
    text_arr = [x.replace("\n", "") for x in text_arr]
    text_arr = [n for n in text_arr if not n.isspace()]
    text_arr = [x.strip() for x in text_arr]
    return text_arr
