import urllib.request as urllib2
import requests
from bs4 import BeautifulSoup
from time import sleep
import os
import sys
import argparse
import PyPDF2 as pypdf2
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.110 Safari/537.36'}


#Name, Author, Year, Source, Type, Link

def get_urls(url, location):
    request = requests.get(url)#, HEADERS)
    print('Status Code', request.status_code)
    soup = BeautifulSoup(request.content, "html.parser")

    meta_data = dict()
    urls = []
    names = []
    authors = []
    year = []
    source = []
    pdf_names = []
    #base_url = os.getcwd() ##############################################################
    i = 0

    for each in soup.findAll(class_='title is-5 mathjax'):
      val = each.get_text().replace('\n', '').strip().encode()
      pdf_names.append(val.replace(':', '')+'.pdf')
      names.append(val)


    for each in soup.find_all(class_='authors'):
      auth = ''
      for each1 in each.find_all('a'):
        auth += each1.get_text()+', '
      authors.append(auth[:-2])
      year.append(2018)
      source.append('Cornell University Library arxiv.org')   #YEAR = 2018, type='pdf', source='arxiv.org'

    for each in soup.find_all(class_="list-title level-left"):
      dd = {}
      urls.append((each.find('a')['href'], pdf_names[i], names[i], authors[i],
                  year[i], source[i]))
      #print(urls)
      dd['name'] = names[i]
      dd['author'] = authors[i]
      dd['year'] = year[i]
      dd['source'] = source[i]
      dd['language'] = 'English'
      dd['type'] = 'pdf'
      dd['link'] = os.path.join(location, pdf_names[i]) ################################## CHANGE
      meta_data[names[i]] = dd
      i += 1

    return urls, meta_data


def download(urls, path):
    old_dir = os.getcwd()
    os.chdir(path)
    for each in urls:
        name = each[1]
        url = each[0]
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
        sleep(1000) #1 Second
    os.chdir(old_dir)


def main():
    meta_data = dict()

    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Topic to Search Research Papers.")
    args = parser.parse_args()

    topic = '+'.join(args.url.lower().split(' '))

    path = os.path.join(os.getcwd(), 'PDFs')
    if not os.path.exists(path):
        os.makedirs(path)
    
    for i in range(1): #Increments by 50
      if(i == 0):
          url = 'https://arxiv.org/search/?query='+topic+'&searchtype=all&source=header&start=0'
          #url = 'https://scholar.google.com/scholar?q='+topic+'+Research+papers&hl=en&as_sdt=0&as_vis=1&oi=scholart'
      else:
          url = 'https://arxiv.org/search/?query='+topic+'&searchtype=all&source=header&start='+str(i)
          #url = 'https://scholar.google.com/scholar?start='+str(i)+'&q='+topic+'Research+papers&hl=en&as_sdt=0,5&as_vis=1'
      print(url)
      urls, meta_d = get_urls(url, path)
      #print(urls)
      download(urls, path)
      meta_data = dict(meta_data, **meta_d)
      print('\n')

    return_dic = {"meta": meta_data}
    with open('metadata_pdf.json', 'w') as file:
        file.write(json.dumps(return_dic))

if __name__ == "__main__":
    main()