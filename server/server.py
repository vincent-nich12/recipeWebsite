###################### External functions #######################

from flask import Flask, render_template, request, flash, redirect, url_for, abort
import psycopg2
import traceback
import os
from werkzeug.utils import secure_filename
import pickle
import re
from utils.database_utils.DatabaseConnector import DatabaseConnector
from utils.searchers.RecipeSearcher import RecipeSearcher
from utils.database_utils.SQLRunner import SQLRunner
from utils.common.recipe import Recipe
from utils.common.categories import Categories
from utils.common.general_utils import upload_file

#################################################################

####################### Prerequisites ###########################
UPLOAD_FOLDER = '/root/recipeWebsite/server/static/'
ALLOWED_EXTENSIONS = ['.gif','.png','.jpg','.jpeg']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

@app.before_request
def limit_remote_addr():
    if request.remote_addr != '151.228.104.197':
        abort(403)

databaseConnector = DatabaseConnector()
sqlRunner = SQLRunner(databaseConnector)
#################################################################

###################Functions to load webpages ###################
#Homepage
@app.route('/')
def home():
	#open website
    return render_template('Recipe_Home.html')

#Load the add a recipe page
@app.route('/Add_a_Recipe.html')
def addRecipes():
	return render_template('Add_a_Recipe.html')

#Search for a recipe by name
@app.route('/Recipe_Search.html', methods=['GET'])
def searchRecipe():
    try:
        #The value to search
        searchValue = request.args['recipesearch']
        #Connect to database
        databaseConnector.connect()
        #Get all the recipes and order by similarity
        #returned as a list of Recipe objects
        recipeSearcher = RecipeSearcher(sqlRunner,searchValue,10)
        recipes = recipeSearcher.search_recipes()
        return render_template('Recipe_Search.html',recipes=recipes)
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html',emsg = 'An unexpected error occured, please try again later.', error = e)
    finally:
        databaseConnector.close_connection()

#Search for a recipe by category
@app.route('/Category_Search.html')
def searchCategory():
	return render_template('Category_Search.html')

#Page Rendered when a recipe is sent for previewing
@app.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        #Create a Recipes object
        recipe = Recipe.create_recipe_object_from_website(request,databaseConnector)
        #Image upload handler
        file_URL = upload_file(app,request,recipe.recipe_id,ALLOWED_EXTENSIONS)
        recipe.image_URL = file_URL
        #Create the categories object
        categories = Categories.create_categories_object_from_website(request,recipe.recipe_id)
        #Save the details temporarly into a pickle file
        with open('newItems.pkl', 'wb') as f:
            pickle.dump([recipe,categories],f)

        return render_template('Preview_Recipe.html',recipe=recipe,categories=categories)
		
    except Exception as e:
        #print(e)
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()

#Function called by the preview page to submit the recipes 
@app.route('/Submitted_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        #Submit everything to the database
        databaseConnector.connect()
        
        #load previous variables
        file = open('newItems.pkl','rb')
        data = pickle.load(file)
        file.close()
        
        #Order of variables in data.
        #[newID,recipeTitle,mealString,skillLevelString,servings,hours,minutes,
        #categories,ingredients,method,notes,file_URL]
        
        mealCats = [data[0]] #add the ID
        #Add all the categories (7 because thats the index of the categories)
        for x in data[7]:
            mealCats.append(x)
            
        #Initialise list
        recipeToAdd = [0]*len(data)
        recipeToAdd[0] = data[0] #add a new ID
        recipeToAdd[7] = data[0] #add the category ID
        
        for x in range(0,len(data)):
            if x == 7 or x == 0:
                continue
            recipeToAdd[x] = data[x]
        
        
        #Add the category type
        databaseConnector.cur.execute('INSERT INTO meal_cats VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',mealCats)
        #Add the recipe
        databaseConnector.cur.execute('INSERT INTO recipes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',recipeToAdd)
               
        databaseConnector.commit_changes()
        
        return render_template('Submitted_Recipe.html',error=None, recipeTitle=recipeToAdd[1],mealString=recipeToAdd[2],skillLevelString=recipeToAdd[3],servings=recipeToAdd[4],hours=recipeToAdd[5],minutes=recipeToAdd[6],categories=recipeToAdd[7],ingredients=recipeToAdd[8],method=recipeToAdd[9],notes=recipeToAdd[10],file_URL=recipeToAdd[11])
    except Exception as e:
        traceback.print_exc()
        return render_template('Submitted_Recipe.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()

#Favourites Page
@app.route('/Favourites.html')
def favs():
	return render_template('Favourites.html')

#Search for a recipe by ingredients
@app.route('/Ingredient_Search.html')
def ingredientSearch():
	return render_template('Ingredient_Search.html')
    
#Recipe Search Result
@app.route('/Recipe_Result.html',methods=['GET'])
def recipeResult():
    try:
        #get the recipe name
        recipeName = request.args.get('recipeName')
        databaseConnector.connect()
        recipeAtts = sqlRunner.run_script('SELECT * FROM recipes INNER JOIN meal_cats ON \
                                           recipes.meal_cat_id = meal_cats.meal_cat_id WHERE \
                                           recipes.recipe_name = %s', [recipeName])
        recipeAtts = recipeAtts[0]
        # Construct the recipe object
        recipe = Recipe.construct_recipe(recipeAtts,True)
        # Remove the recipe atts and only use the category atts 
        recipeAtts = recipeAtts[Recipe.get_num_atts():len(recipeAtts)]
        # Construct the categories object
        categories = Categories.construct_categories_for_recipe(recipeAtts)
        return render_template('Recipe_Result.html',recipe=recipe,categories=categories.get_categories_as_list())
    except Exception as e:
        traceback.print_exc()
        return render_template('Recipe_Home.html', error='Error!', emsg=e)
    finally:
        databaseConnector.close_connection()
	
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")