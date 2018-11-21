import urllib.request as urllib2
import requests
from bs4 import BeautifulSoup
from time import sleep
import os
import sys
import argparse
from docx import Document
from docx.shared import Inches
import PyPDF2 as pypdf2

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}


def get_urls(url):
    request = requests.get(url, HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    urls = []
    names = []
    base_url = os.path.dirname(url)
    i = 0

    for each in soup.findAll(class_='gs_rt'):
    	names.append(each.find('a').get_text().replace(':', '').replace('?', '')+'.pdf')

    for anchor in soup.findAll(class_='gs_or_ggsm'): #Going inside links
        urls.append((names[i], anchor.find('a')['href']))
        i += 1
    return urls


def convert_to_word(name):
    pdfFileObject = open(name, 'rb')
    pdfReader = pypdf2.PdfFileReader(pdfFileObject)
    document = Document()
    count = pdfReader.numPages
    for i in range(count):
        page = pdfReader.getPage(i)
        document.add_paragraph(page.extractText())
    document.save('Demo1.docx')

def download(urls, path):
    old_dir = os.getcwd()
    os.chdir(path)
    for name, url in urls:
        if os.path.isfile(name):
            print("already exists, skipping...")
            continue
        try:
            request = urllib2.Request(url)
            res = urllib2.urlopen(request).read()
            with open(name, 'wb') as pdf:
                pdf.write(res)
            print("Downloaded", name)
        except Exception as e:
            print("Failed to download because of", e)
    os.chdir(old_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Topic to Search on Google.")
    args = parser.parse_args()

    topic = '+'.join(args.url.lower().split(' '))

    path = os.path.join(os.getcwd(), 'Downloaded')
    if not os.path.exists(path):
        os.makedirs(path)
    
    for i in range(0, 30, 10):
	    if(i == 0):
	    	url = 'https://scholar.google.com/scholar?q='+topic+'+Research+papers&hl=en&as_sdt=0&as_vis=1&oi=scholart'
	    else:
	    	url = 'https://scholar.google.com/scholar?start='+str(i)+'&q='+topic+'Research+papers&hl=en&as_sdt=0,5&as_vis=1'

	    print(url)
	    download(get_urls(url), path)
	    print('\n')

if __name__ == "__main__":
    main()
