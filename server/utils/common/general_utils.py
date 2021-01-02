import os
import json
from shutil import copy2

"""
Function for reading a file given a directory.
NOTE that the directory must be absolute for this to work
correctly.
"""
def open_file(aFile):
    with open(aFile) as inFile:
        list = inFile.readlines()
    return list
    
"""
Function to load the config file of the server (stored as a JSON file).
"""
def open_config_file(config_file_path):
    with open(config_file_path) as json_file:
        data = json.load(json_file)
    return data

"""    
Function to upload a recipe image onto the server. For 
previewing purposes, the file is stored under the name "temp".

Params are the config file object and the request object.
"""
def upload_recipe_image(config,request):
    ALLOWED_EXTENSIONS = config['image_uploading']['allowed_extensions']
    if request.method == 'POST':
        #Check if file has actually been uploaded
        if 'upload' not in request.files:
            return None
        file = request.files['upload']
		
        #If user does not select file, then it is submitted as an empty string
        if file.filename == '':
            return None
		
        name, extension = os.path.splitext(file.filename)
        # if the file type is valid
        if extension.lower() in ALLOWED_EXTENSIONS:
            saveLocation = os.path.join(config['image_uploading']['img_upload_folder'],"temp") + extension
            file.save(saveLocation)
            return saveLocation
        else:
            errorStr = ''
            for i in range(len(ALLOWED_EXTENSIONS)):
                if i == (len(ALLOWED_EXTENSIONS) - 1):
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i]
                else:
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i] + ','
            raise Exception(extension + ' found, only' + errorStr + ' allowed.')
    
"""
This function is called when the user wants to save the recipe onto the server.
It copies the temp file and saves it. The img's name is simply the recipe_id.
"""    
def copy_temp_img_file(config,recipe):
    if recipe.image_URL is None:
        return None
    name, extension = os.path.splitext(recipe.image_URL)
    tempFileLoc = recipe.image_URL
    newFileLoc = config['image_uploading']['img_upload_folder'] + str(recipe.recipe_id) + extension
    copy2(tempFileLoc, newFileLoc)
    return newFileLoc