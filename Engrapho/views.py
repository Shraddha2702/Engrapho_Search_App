from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug import secure_filename
from lxml import etree
from PyPDF2 import PdfFileReader
from pymongo import MongoClient
import os, subprocess, sys, docx

app = Flask(__name__)
app.secret_key = os.urandom(16)
UPLOAD_FOLDER ='Files'
ALLOWED_EXTENSIONS = ['docx', 'pptx', 'mp3', 'pdf', 'epub', 'djvu']
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["XML_FILE"]='project_index.xml'
g.db = MongoClient('localhost','27017').test_database
g.collection_main = g.db.test_collection()
g.collection_inverted = g.db.test_inverted_collection()

@app.route('/',methods=["POST","GET"])

#Display the search page.
def display():
    content={}
    if 'messages' in session:
        content=session['messages']
    return render_template('index.html', content=content)

@app.route('/login',methods=["POST","GET"])

#Display Login page.
def login():
    if request.method == "POST":
        if request.form["username"]=="Bharath":
            session["logged_in"] = True
            return redirect(url_for('add_documents'))
    return render_template('login.html')


@app.route('/search', methods=["POST", "GET"])

# This function searches for the given keyword.
def search():
    if request.method == 'POST':
        #The search process is done here.
        search_items = request.form['search'].strip().split(' ')
        ids=[]
        locations=[]
        file_types_selected = request.form.getlist('choices-single-defaul')
        for i in search_items:
            cursor = g.collection_inverted.find({'index':i})
            for j in cursor:
                ids = ids+j['ids']
        ids = list(set(ids))
        for i in ids:
            cursor = g.collection_main.find({'_id':i})
            for j in cursor:
                locations.append(str(j['location']))
        session['messages']=locations
    return redirect(url_for('display'))

@app.route('/add',methods=["POST","GET"])
def add_documents():

    # This function updates the inverted indexes file.
    def prepocess(meta_data, id):
        indexes = meta_data['title'].split(' ') + meta_data['author'].split(' ') + meta_data['subtype'].split(' ')
        print("the indexes are", indexes)
        for i in indexes:
            g.collection_inverted.update({'index':i},{'$push':{'ids':{'$each':[id]}}})



    # This function updates mongodb main file.
    def createOrUpdateBook(meta_data):
        #uploading to the main database.
        id = g.collection_main.insert(meta_data)
        prepocess(meta_data, id)


    # This function extracts meta-data from the file.
    def extractData(extension,location):
        meta_data={'location':location,
                    'extension':extension
                    }
        if extension=='pdf':
            print(location)
            with open(location,'rb') as f:
                pdf_to_get = PdfFileReader(f)
                file_info = pdf_to_get.getDocumentInfo()
                print(file_info)
                meta_data['author']=file_info['/Author'] if '/Author' in file_info else ''
                meta_data['bookname']=file_info['/Title'] if '/Title' in file_info else os.path.basename(f.name).split('.')[0]
                print(meta_data)
        if extension=='docx' or extension=='docs' or extension=='doc':
            with open(location,'rb') as f:
                # Do the stuff.
                meta_data['author'] = None
                meta_data['bookname'] = None

        if extension=='mp3':
            with open(location,'rb') as f:
                # Do the stuff.
                meta_data['author'] = None
                meta_data['title'] = None

        if extension=='png' or extension=='jpeg':
            pass


        createOrUpdateBook(meta_data)

    if "logged_in" in session and session["logged_in"]:
        if request.method == "POST":
            for f in request.files.getlist("documents"):
                location=os.path.join(app.config["UPLOAD_FOLDER"],f.filename)
                print(location)
                f.save(location)
                extractData(location.split('.')[-1],location)
                print("add is executed")
        return render_template('add_documents.html')
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.debug=True
    app.run()
