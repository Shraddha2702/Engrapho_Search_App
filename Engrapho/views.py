from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug import secure_filename
from lxml import etree
from PyPDF2 import PdfFileReader
from pymongo import MongoClient
import os, subprocess, sys, docx
import requests
from bs4 import BeautifulSoup
import micawber

from fetch_youtube_ebook_links import *

app = Flask(__name__)
app.secret_key = os.urandom(16)
UPLOAD_FOLDER ='Files'
ALLOWED_EXTENSIONS = ['docx', 'pptx', 'mp3', 'pdf', 'epub', 'djvu']

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["XML_FILE"]='project_index.xml'
db = MongoClient('localhost',27017).test_database
collection_main = db.test_collection
collection_inverted = db.test_inverted_collection

@app.route('/',methods=["POST","GET"])
#Display the search page.
def display():
    content={}
    if 'messages' in session:
        content['messages']=session['messages']
        content['extensions']=session['extensions']
        content['authors']=session['authors']
        content['youtube']=session['youtube']
        content['ebook']=session['ebook']
        content['sources']=session['sources']
    #print(content)
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
        term = request.form['search'].strip()
        search_items = request.form['search'].strip().split(' ')
        print(search_items)
        print('---------------'+"extensions"+'----------------')
        file_extensions = request.form.getlist('extensions')
        print(file_extensions)
        print('---------------'+"authors"+'-------------------')
        file_authors = request.form.getlist('authors')
        print(file_authors)

        ids=[]
        locations=[]
        # Searching the inverted indexes.
        for i in search_items:
            cursor = collection_inverted.find({'index':i}) if i else []
            for j in cursor:
                ids = ids+j['ids']
        ids = list(set(ids))
        print(ids)
        extensions = set()
        authors = set()
        #Searching the main table.
        for i in ids:
            cursor = collection_main.find({'_id':i})
            for j in cursor:
                print('PRINTING THE CURSOR--------')
                print(j)
                j.pop('_id')
                extensions.add(j['extension'])
                authors.add(j['author'])
                # Checking if the file_extensions are checked.
                if file_extensions or file_authors:
                    if (file_extensions and j['extension'] in file_extensions) or (file_authors and j['author'] in file_authors):
                        print('DOING IF EXTENSIONS')
                        locations.append(j)
                else:
                    print('DOING ELSE')
                    locations.append(j)
        session['messages']=locations
        session['extensions']=list(extensions)
        session['authors']=list(authors)
        
        sources = []
        for i in range(len(session['messages'])):
            if(session['messages'][i]['extension'] == 'pdf'):
                sources.append('Google Scholar')
                session['messages'][i]['source'] = 'Google Scholar'
            else:
                sources.append('LinkedIn Slideshare')
                session['messages'][i]['source'] = 'LinkedIn Slideshare'

        session['sources']=list(set(sources))

        ############YOUTUBE AND EBOOK PART
        topic = '+'.join(term.lower().split(' '))

        base_url = 'https://youtube.com'
        youtube_url = 'https://www.youtube.com/results?search_query='+topic
        dic_yt = youtube_inf(youtube_url, base_url)
        print('youtube added to Session')
        session['youtube'] = dic_yt

        base_url2 = 'https://worldcat.org'
        ebook_url = 'https://www.worldcat.org/search?qt=worldcat_org_all&q='+topic+'#%2528x0%253Abook%2Bx4%253Adigital%2529format' 
        dic_ebook = ebook_inf(ebook_url, base_url2)
        print('ebook added to Session')
        session['ebook'] = dic_ebook
        session['messages'] += dic_ebook

        book = list(set([each['extension'] for each in dic_ebook]))
        for one in book:
            session['extensions'].append(one)

        autt = list(set([each['author'] for each in dic_ebook]))
        for two in autt:
            session['authors'].append(two)

        sour = list(set(each['source'] for each in dic_ebook))
        for three in sour:
            session['sources'].append(three)

        #################################### --------------- Add PPT Section and
        #################################### --------------- Replace Empty string with 'Not Available'
        print('---'*10+'messages')
        #print(session['messages'])
        #print('--'*10)
        print('Session done === Sending')
    return redirect(url_for('display'))

@app.route('/add',methods=["POST","GET"])
def add_documents():

    # This function updates the inverted indexes file.
    def prepocess(meta_data, id):
        indexes = meta_data['bookname'].split(' ') + meta_data['author'].split(' ') #+ meta_data['subtype'].split(' ')
        print("the indexes are", indexes)
        for i in indexes:
            collection_inverted.update({'index':i},{'$push':{'ids':{'$each':[id]}}},True)



    # This function updates mongodb main file.
    def createOrUpdateBook(meta_data):
        #uploading to the main database.
        id = collection_main.insert(meta_data)
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
                zf = zipfile.ZipFile(location)
                doc = lxml.etree.fromstring(zf.read('docProps/core.xml'))
                ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                if doc.xpath('//dc:creator', namespaces=ns)[0].text:
                    meta_data['author'] = doc.xpath('//dc:creator', namespaces=ns)[0].text
                else:
                    meta_data['author'] = ''
                if doc.xpath('//dc:title', namespaces=ns)[0].text:
                    meta_data['bookname'] = doc.xpath('//dc:title', namespaces=ns)[0].text
                else:
                    meta_data['bookname'] = os.path.basename(meta_data['location']).split('.')[0]

        ########################## --------------- ADD CODE FOR PPTX Files To EXTRACT DATA
        ########################## --------------- ALSO, SEARCH FOR META-DATA FILE WHEN ADDING DATA


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
