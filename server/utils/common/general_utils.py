import os
import json

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
Function to upload a file onto the server.

Params are the config file object, the request object, the ID and an array
of valid extensions for the image file.

"""
def upload_file(config,request,ID):
    ALLOWED_EXTENSIONS = config['misc']['allowed_extensions']
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
            file.save(os.path.join(config['misc']['img_upload_folder'],filename))
            return 'static/' + filename
        else:
            errorStr = ''
            for i in range(len(ALLOWED_EXTENSIONS)):
                if i == (len(ALLOWED_EXTENSIONS) - 1):
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i]
                else:
                    errorStr = errorStr + ' ' + ALLOWED_EXTENSIONS[i] + ','
            raise Exception(file_extension + ' found, only' + errorStr + ' allowed.')