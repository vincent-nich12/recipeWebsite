import os

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
Function to upload a file onto the server.

Params are the app object, the request object, the ID and an array
of valid extensions for the image file.

"""
def upload_file(app,request,ID,ALLOWED_EXTENSIONS):
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