import os, re, sys
from porterstemmer import PorterStemmer

stopwords = []
with open('stopwords', 'r') as stopwordfile:
	stopwords = stopwordfile.read()

# Tokenize text with different rules
def tokenizeText(input_words):
	
	output_words = []

	for word in input_words.split():

		#Convert to lowercase
		tempword = word.lower()

		#Apostrophe cases 

		#'let's
		tempword = tempword.replace("let's", "let us")
		#'are'
		tempword = tempword.replace("'re", " are")
		#'will'
		tempword = tempword.replace("'ll", "  will")
		#'have'
		tempword = tempword.replace("'ve", " have")
		#'would'
		tempword = tempword.replace("'d", " would")
		#'am'
		tempword = tempword.replace("'m", " am")
		#'not'
		tempword = tempword.replace("n't", " not")
		#'of'
		tempword = tempword.replace("o'", "of")
		#'are'
		tempword = tempword.replace("y'", "you ")


		#Periods, exclamations, question marks at the end of sentences
		tempword = tempword.replace('.', '')
		tempword = tempword.replace('?', '')
		tempword = tempword.replace('!', '')
		tempword = tempword.replace(',', '')


		#Remove parentheses
		tempword = tempword.replace('(', '')
		tempword = tempword.replace(')', '')

		#Remove single and double quotes
		tempword = tempword.replace("'", '')
		tempword = tempword.replace('"', '')
		
		#Remove single periods, spaces, 
		if tempword != '.' and tempword != ' ':

			output_words.append(tempword)


	return output_words


#Remove stopwords
def removeStopwords(input_tokens, stopwords):

	output_tokens = []

	for word in input_tokens:

		stopword_true = False
		for stopword in stopwords.split():

			if word == stopword:

				stopword_true = True
				break
		if stopword_true == False:
			output_tokens.append(word)

	return output_tokens

#Stem words
def stemWords(input_tokens):

	stemmer = PorterStemmer()
	stemmed_words = []
	for token in input_tokens:
		stemmed_words.append(str(stemmer.stem(token, 0, len(token)-1)))

	return stemmed_words

# Function preprocesses content and returns an ordered list of tokens
def preprocess(doc_content):

	tokens = tokenizeText(doc_content)
	without_stopwords = removeStopwords(tokens, stopwords)
	stemmed = stemWords(tokens)
	return stemmed
