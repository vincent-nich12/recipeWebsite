"""
Function for reading a file given a directory.
NOTE that the directory must be absolute for this to work
correctly.
"""
def open_file(aFile):
    with open(aFile) as inFile:
        list = inFile.readlines()
    return list