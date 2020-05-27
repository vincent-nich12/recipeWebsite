###################### External functions #######################

from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import traceback
import os
from werkzeug.utils import secure_filename
import pickle

#################################################################

####################### Prerequisites ###########################
UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = ['.gif','.png','.jpg','.jpeg']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#################################################################

###################Functions to load webpages ###################
#Homepage
@app.route('/')
def home():
	#open website
	return render_template('Recipe_Home.html')

#Add a recipe
@app.route('/Add_a_Recipe.html')
def addRecipes():
	return render_template('Add_a_Recipe.html')

#Search for a recipe by name
@app.route('/Recipe_Search.html')
def searchRecipe():
	return render_template('Recipe_Search.html')

#Search for a recipe by category
@app.route('/Category_Search.html')
def searchCategory():
	return render_template('Category_Search.html')

#Page Rendered when a recipe is added to the database (or attempted)
@app.route('/Preview_Recipe.html', methods=['POST'])
def previewRecipe():
    try:
        conn = None

        #Recipe title
        recipeTitle = request.form['recipe_name']
        #Breakfast, Lunch, Dinner, Dessert or Snacks
        mealString = request.form['meal']
        #Easy, Medium or Hard
        skillLevelString = request.form['skill_level']
        #Number of servings
        servings = request.form['servings']
        #Time taken to complete the recipe
        hours = request.form['hours']
        minutes = request.form['minutes']

        #CheckBoxes for categories
        pasta = (request.form.get('Pasta') is not None)
        spicy = (request.form.get('Spicy') is not None)
        rice = (request.form.get('Rice') is not None)
        noodles = (request.form.get('Noodles') is not None)
        baked = (request.form.get('Baking') is not None)
        pie = (request.form.get('Pie') is not None)
        vegetarian = (request.form.get('Vegetarian') is not None)
        one_pot = (request.form.get('One Pot') is not None)
        cake = (request.form.get('Cake') is not None)
        
        categories = [pasta,spicy,rice,noodles,baked,pie,vegetarian,one_pot,cake]

        #Ingredients textbox 
        ingredients = request.form['ingredients']
        #Split by new line.
        ingredients = ingredients.replace(',','\n')
        ingredients = ingredients.split('\n')
        #Remove \r characters
        for x in ingredients:
            if x == '\r':
                ingredients.remove(x)
                
        #Method textbox
        method = request.form['Method']
        #Split by new line.
        method = method.replace(',','\n')
        method = method.split('\n')
        #Remove \r characters
        for x in method:
            if x == '\r':
                method.remove(x)
                
        #Notes textbox
        notes = request.form['notes']
        #Split by new line.
        notes = notes.split('\n')
        #Remove \r characters
        for x in notes:
            if x == '\r':
                notes.remove(x)

        conn = getConn()
        cur = conn.cursor()

        #Generate the IDs for the new recipe
        ##########################################################
        cur.execute('SET search_path to public')
        cur.execute('SELECT * FROM recipes')
        rows = cur.fetchall()
		
        numRecords = 0
        numRecords = len(rows)
            
        newID = numRecords + 1
        ##########################################################
        #Image upload handler
        file_URL = upload_file(request,newID)

        #Save the details temporarly into a pickle file
        with open('newItems.pkl', 'wb') as f:
            pickle.dump([newID,recipeTitle,mealString,skillLevelString,servings,hours,minutes,categories,ingredients,method,notes,file_URL],f)

        return render_template('Preview_Recipe.html',recipeTitle=recipeTitle,mealString=mealString,skillLevelString=skillLevelString,servings=servings,hours=hours,minutes=minutes,categories=categories,ingredients=ingredients,method=method,notes=notes,file_URL=file_URL)
		
    except Exception as e:
        #print(e)
        traceback.print_exc()
        return render_template('Added_Recipe_Error.html', error='Error!', emsg=e)
    finally:
        if conn:
            conn.close()

#Function called by the preview page to submit the recipes 
@app.route('/Submitted_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        #Submit everything to the database
        conn = None
        
        conn = getConn()
        cur = conn.cursor()
        
        #load previous variables
        file = open('newItems.pkl','rb')
        data = pickle.load(file)
        file.close()
        
        #Order of variables in data.
        #[newID,recipeTitle,mealString,skillLevelString,servings,hours,minutes,
        #categories,ingredients,method,notes,file_URL]
        cur.execute('SET search_path to public')
        
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
        cur.execute('INSERT INTO meal_cats VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',mealCats)
        #Add the recipe
        cur.execute('INSERT INTO recipes VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',recipeToAdd)
               
        conn.commit()
        
        return render_template('Submitted_Recipe.html',error=None)
    except Exception as e:
        traceback.print_exc()
        return render_template('Submitted_Recipe.html', error='Error!', emsg=e)
    finally:
        if conn:
            conn.close()
    
	

#Favourites Page
@app.route('/Favourites.html')
def favs():
	return render_template('Favourites.html')

#Search for a recipe by ingredients
@app.route('/Ingredient_Search.html')
def ingredientSearch():
	return render_template('Ingredient_Search.html')
    
#Recipe Search Result
@app.route('/Recipe_Result.html')
def recipeResult():
	return render_template('Recipe_Result.html')
	
#################################################################

########################## Helper Functions #####################
#Function to open a file
def openFile(aFile):
	with open(aFile) as inFile:
		list = inFile.readlines()
	return list
	
#Function to get the connection to the database
def getConn():
	list = openFile('database_access.txt')
	dbname = list[0]
	user = list[1]
	password = list[2]
	
	connStr = ("dbname = " + dbname +  "user=" + user + " password=" + password)
	
	conn= psycopg2.connect(connStr)
	return conn
	
#Function to upload a file onto the server
def upload_file(request,ID):
    if request.method == 'POST':
        #Check if file has actually been uploaded
        if 'upload' not in request.files:
            return None
        file = request.files['upload']
		
        #If user does not select file, then its submitted as an empty string
        if file.filename == '':
            return None
		
        filename, file_extension = os.path.splitext(file.filename)
        if file and (file_extension.lower() in ALLOWED_EXTENSIONS):
            filename = str(ID) + file_extension.lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            return os.path.join(app.config['UPLOAD_FOLDER'],filename)
        else:
            errorStr = ''
            for i in range(len(ALLOWED_EXTENSIONS)):
                if i == (len(ALLOWED_EXTENSIONS) - 1):
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i]
                else:
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i] + ','
            raise Exception(file_extension + ' found, only' + errorStr + ' allowed.')
		
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
#################################################################