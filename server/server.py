from flask import Flask, render_template,request

app = Flask(__name__)

#Homepage
@app.route('/')
def home():
    return render_template('index.html')

#Function to open a file
def openFile(aFile):
	with open(aFile) as inFile:
		list = inFile.readlines()
	return list

if __name__ == '__main__':
    
    app.run(debug=True, host="0.0.0.0")