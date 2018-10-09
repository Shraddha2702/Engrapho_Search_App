from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug import secure_filename
from lxml import etree
from PyPDF2 import PdfFileReader
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)
UPLOAD_FOLDER = os.getcwd()+'\Files'
ALLOWED_EXTENSIONS = ['docx', 'pptx', 'mp3', 'pdf', 'epub', 'djvu']
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["XML_FILE"]='project_index.xml'

@app.route('/',methods=["POST","GET"])
def display():
    content={}
    if 'messages' in session:
        content=session['messages']
        session['messages']=[]
    return render_template('index.html', content=content)

@app.route('/login',methods=["POST","GET"])
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
        location=[]
        search_item = request.form['search'].strip()
        file_types_selected = request.form.getlist('choices-single-defaul')
        xml_file = etree.parse('project_index.xml')
        for fType in file_types_selected:
            fType=fType.lower()
            name_as_title = xml_file.xpath("//book[title/text()='"+ search_item +"']/type[@extension='"+ fType +"']/location/text()")
            name_as_author = xml_file.xpath("//book[author/text()='"+ search_item +"']/type[@extension='"+ fType +"']/location/text()")
            location.append(name_as_title)
            location.append(name_as_author)
        session['messages']=location
    return redirect(url_for('display'))

@app.route('/add',methods=["POST","GET"])
def add_documents():

    # This function updates xml file.
    def createOrUpdateBook(meta_data):
        xml_parsed_file = etree.parse(app.config["XML_FILE"])
        xml_file = xml_parsed_file.getroot()
        book_elements = xml_parsed_file.xpath("//book[title/text()='"+ meta_data['bookname'] +"' and author/text()='"+ meta_data['author'] +"']")
        print(book_elements)
        if book_elements:
            root = book_elements[0]
        else:
            book = etree.SubElement(xml_file,'book')
            title = etree.SubElement(book, 'title')
            title.text = meta_data['bookname']
            author = etree.SubElement(book, 'author')
            author.text = meta_data['author']
            root = book

        fileType = etree.SubElement(root,'type')
        fileType.attrib['extension'] = meta_data['extension']
        location = etree.SubElement(fileType, 'location')
        location.text = meta_data['location']

        xmlFile = etree.ElementTree(xml_file)
        xmlFile.write(app.config["XML_FILE"], pretty_print=True,xml_declaration=True)

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
                meta_data['author']=file_info['/Author']
                meta_data['bookname']=file_info['/Title'] if '/Title' in file_info else os.path.basename(f.name)

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
