"""
Author: Shraddha Kulkarni (6117-9554-57)
1. Load the dataset into firebase using requests
2. Create dictionary and add id's for the keyword
"""
import requests
import json

def main():
	#PART 1 Loading the data into firebase
	with open('prize.json', 'r') as f:
		data = json.load(f)

	url = 'https://inf551-43cab.firebaseio.com/.json'
	data_upload = json.dumps(data)
	req1 = requests.put(url, data=data_upload)
	print("Response to upload prizes.json : ",req1)

	#PART 2 Creating Dictionary
	#Have created a new extract_stopwords.py class which extracts all the keywords from the website and returns a list of Stopword Keywords
	#final_list = extract_stopwords.main() #To get all stopwords
	with open('stopwords.txt', 'r') as f:
		content = f.readlines()

    # you may also want to remove whitespace characters like `\n` at the end of each line
	final_list = [x.strip() for x in content]
	punc = [",", ";", ".", "/","\"", "$", "%", "^", "&", "*", "(", ")", "-","_", "+", "=", "{", "}","[", "]", "*", ";", "?","<i>","</i>","#"]
	final_list.append(punc)
	
	#Get the prizes.json from Firebase for creating the dictionary
	urll = 'https://inf551-43cab.firebaseio.com/prizes.json'
	response1 = requests.get(urll)
	
	worddict = dict()
	abb = json.loads(response1.text)
	for elem in abb:
	    for each in elem['laureates']:
	    	if('motivation' in each.keys()):
	            sentence = each['motivation']
	            words = sentence.split()
	            idd = each['id']
	            
	            for word in words:
	                word = word.lower()
	                for punn in punc: word = word.strip(punn)
	                if ((word not in final_list) and (word not in worddict.keys()) and (word != "")):
	                    worddict[word] = []
	                    worddict[word].append(idd)
	                elif (word in worddict.keys()):
	                    worddict[word].append(idd)

	
	#Uploading the dictionary to Firebase
	url2 = 'https://inf551-43cab.firebaseio.com/.json'
	dictreturn = {"index": worddict}
	dicc = json.dumps(dictreturn)
	req2 = requests.patch(url2, data=dicc)
	print("Response to upload index.json : ", req2)

if __name__ == '__main__':
	main()