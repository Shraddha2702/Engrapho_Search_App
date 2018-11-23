import requests
from bs4 import BeautifulSoup
import os
import json
import micawber
import sys
import argparse

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}


def youtube_inf(url, base_url):
	request = requests.get(url, HEADERS)
	soup = BeautifulSoup(request.content, 'html.parser')

	youtube_urls = []

	for each in soup.findAll('a', {'class':' yt-uix-sessionlink spf-link '}):
	    youtube_urls.append(base_url+each['href'])


	#For getting the Youtube links
	youtube_video_infos = []

	for every_link in youtube_urls:
		providers = micawber.bootstrap_basic()
		info = providers.request(every_link)
		youtube_video_infos.append((info['author_name'],
			info['thumbnail_url'], info['title'],
			info['url']))

	#print(youtube_video_infos)
	with open('metadata_youtube.txt', 'w') as file:
	    file.write(str(youtube_video_infos))



#EBooks
def ebook_inf(url2, base_url2):
	request2 = requests.get(url2, HEADERS)
	soup2 = BeautifulSoup(request2.content, 'html.parser')

	names = []
	authors = []
	years = []
	sources = []
	links = []

	meta_data = dict()

	for each in soup2.find_all(class_='name'):
	    names.append(each.find('a').get_text())
	    links.append(base_url2+each.find('a')['href'])

	for each_author in soup2.find_all(class_='author'):
	    authors.append(each_author.get_text()[3:])

	for year in soup2.find_all(class_='publisher'):
	    text = year.get_text()
	    years.append(text[-5:].replace(' ', '').replace('.', '').replace(']',''))

	for publish in soup2.find_all(class_='publisher'):
	    sources.append(publish.get_text()[11:])

	for i in range(len(names)):
		dd = dict()
		dd['name'] = names[i]
		dd['author'] = authors[i]
		dd['year'] = years[i]
		dd['source'] = sources[i]
		dd['language'] = 'English'
		dd['type'] = 'eBook'
		dd['link'] = links[i]
		meta_data[dd['name']] = dd


	return_dic = {'meta': meta_data}
	with open('metadata_ebook.json', 'w') as file:
	    file.write(json.dumps(return_dic))



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('url', help='Topic to Search eBooks and Videos.')
	args = parser.parse_args()


	topic = '+'.join(args.url.lower().split(' '))

	base_url = 'https://youtube.com'
	youtube_url = 'https://www.youtube.com/results?search_query='+topic
	youtube_inf(youtube_url, base_url)

	base_url2 = 'https://worldcat.org'
	ebook_url = 'https://www.worldcat.org/search?qt=worldcat_org_all&q='+topic+'#%2528x0%253Abook%2Bx4%253Adigital%2529format' 
	ebook_inf(ebook_url, base_url2)

if __name__=='__main__':
	main()