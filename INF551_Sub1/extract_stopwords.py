#Extracts all the stop words and returns a lost
from lxml.html.soupparser import fromstring
from bs4 import BeautifulSoup
import requests

def main():
	url_web = 'https://www.ranks.nl/stopwords'
	html_doc = requests.get(url_web, verify=False)
	soupp = BeautifulSoup(html_doc.text, 'html.parser')

	a = soupp.find('div', id='article10ad6d55aba755640460f888b8287532')
	b = a.find('div', 'panel-body')
	c = b.find('table')
	d = c.find('tbody')
	e = d.find('tr')
	f = e.find_all('td')

	dicc = list()
	for elem in f:
	    dicc.append(str(elem).split('<br/>')[1:-1])
	    dicc.append(str(elem).split('<br/>')[0][17:])
	    dicc.append(str(elem).split('<br/>')[-1][:-5])    
	list1 = flatten(dicc)

	aa = soupp.find('div', id='article058919042e40f5d26c8d9b2d65e9ac0f')
	bb = aa.find('div', 'panel-body')
	cc = bb.find('table')
	dd = cc.find('tbody')
	ee = dd.find_all('td')

	list2 = list()
	for each in ee:
	    list2.append(str(each)[4:-5])
	list1.append(list2)

	aaa = soupp.find('div', id='article9596073f1984a55ce1b34302c20df2be')
	bbb = aaa.find('div', 'panel-body')
	ccc = bbb.find('table')
	ddd = ccc.find('tbody')
	eee = ddd.find('tr')
	fff = eee.find_all('td')

	list3 = list()
	for elem in fff:
	    list3.append(str(elem).split('<br/>')[1:-1])
	    list3.append(str(elem).split('<br/>')[-1][1:4])
	list1.append(list3)

	a1 = soupp.find('div', id='article09e9cfa21e73da42e8e88ea97bc0a432')
	b1 = a1.find('div', 'panel-body')
	c1 = b1.find('table')
	d1 = c1.find('tbody')
	e1 = d1.find('tr')
	f1 = e1.find_all('td')

	list4 = list()
	for elem in f1:
	    list4.append(str(elem).split('<br/>')[1:-1])
	    list4.append(str(elem).split('<br/>')[0][-1])
	    list4.append(str(f[0]).split('<br/>')[-1][:-5])
	list1.append(list4)

	punc = [",", ".", "/", "$", "%", "^", "&", "*", "(", ")", "-","_", "+", "=", "{", "}","[", "]", "*", ";", "?"]

	list1.append(punc)
	final_list = flatten(list1)
	return final_list


def flatten(xs):
    res = []
    def loop(ys):
        for i in ys:
            if isinstance(i, list):
                loop(i)
            else:
                res.append(i)
    loop(xs)
    return res

if __name__ == '__main__':
	main()