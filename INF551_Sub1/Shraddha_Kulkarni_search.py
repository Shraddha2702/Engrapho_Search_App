"""
Author: Shraddha Kulkarni (6117-9554-57)
Searching the word in the dictionary returned
"""
import Shraddha_Kulkarni_load
import requests
import json
import sys

def main():
	strif = sys.argv[1]
	strif = strif.lower()
	wordds = strif.split()

	#Getting the Index dictionary from Firebase
	url = 'https://inf551-43cab.firebaseio.com/index.json'
	response = requests.get(url)
	worddict = json.loads(response.text)

	ids = list()

	for each in wordds:
	    if each in worddict.keys():
	        ids.append(worddict[each])

	idlist = flatten(ids)
	idlist = list(set(idlist))
	print(idlist)
	
	return idlist

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

if __name__ == "__main__":
	main()