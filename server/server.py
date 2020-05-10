###################### External functions #######################

from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2
import traceback
import os
from werkzeug.utils import secure_filename

#################################################################

####################### Prerequisites ###########################
UPLOAD_FOLDER = 'uploads/'
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
@app.route('/Added_Recipe.html', methods=['POST'])
def submitRecipe():
    try:
        conn = None
		
		#Recipe title
        recipeTitle = request.form['recipe_name']
		#Breakfast, Lunch, Dinner, Dessert or Snacks
        mealString = request.form['meal']
		#Easy, Medium or Hard
        skillLevelString = request.form['skill_level']
        #Time taken to complete the recipe
        hours = request.form['hours']
        minutes = request.form['minutes']
		
        #CheckBoxes for categories
        pasta = request.form.get('Pasta')
        spicy = request.form.get('Spicy')
        rice = request.form.get('Rice')
        noodles = request.form.get('Noodles')
        baked = request.form.get('Baking')
        pie = request.form.get('Pie')
        vegetarian = request.form.get('Vegetarian')
        one_pot = request.form.get('One Pot')
        cake = request.form.get('Cake')
        
		#Ingredients textbox 
        ingredients = request.form['ingredients']
		#Method textbox
        method = request.form['Method']
		
        conn = getConn()
        cur = conn.cursor()
		
        #Generate the IDs for the new recipe
        ##########################################################
        cur.execute('SET search_path to public')
        cur.execute('SELECT * FROM recipes')
        rows = cur.fetchall()
		
        numRecords = 0
        numRecords = len(rows)
            
        #raise Exception('Message')
        newID = numRecords + 1
        ##########################################################
        #Image upload handler
        file_URL = upload_file(request,newID)	

        #cur.execute('INSERT INTO Meal_types (Meal_type_ID, Pasta, Spicy, Rice,' \
        #'Noodles, Baked, Pie, Vegetarian, One_pot, Cake) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)', \
        #[])

        conn.commit()

        return render_template('Added_Recipe.html', msg='Recipe Added Successfully!')
		
    except Exception as e:
        #print(e)
        traceback.print_exc()
        return render_template('Added_Recipe.html', error='Recipe Not Added Successfully!', emsg=e)
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