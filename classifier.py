import re, os, sys, preprocessor, pickle
from sklearn.svm import *
from sklearn.preprocessing import *
from sklearn.metrics import accuracy_score
from sklearn.metrics import explained_variance_score
import numpy as np
from util import *
# import pandas as pd

def createVocabDict(mode):

	#Declare dictionary with all words from comments
	corpus_dict = {}

	#Number of words
	word_count = 0

	corpus_filename = "corpus.txt"
	if mode == "test":
		corpus_filename = "corpus_test.txt"
	elif mode == "professor":
		corpus_filename = "corpus_professors.txt"
	elif mode == "professor_test":
		corpus_filename = "corpus_professors_test.txt"

	with open(corpus_filename,"r") as corpus_file:
		corpus = corpus_file.read()
		for word in corpus.split():
			
			#Store each word's index value in feature matrix		
			if word not in corpus_dict:
				corpus_dict[word] = word_count
				word_count += 1	

	return corpus_dict

def generateFeatureMatrixRevLevel(reviews, corpus_dict, num_features):

	numReviews = len(reviews)
	numWords = len(corpus_dict)
	feature_matrix = np.zeros((numReviews, num_features))
	label_matrix = np.zeros(numReviews)


	for index, review in enumerate(reviews):


		reviewMatrix = np.zeros(num_features)

		for word in review['comment']: 				       
			if word in corpus_dict:
				reviewMatrix[corpus_dict[word]] += 1
				
		#Normalize
		reviewMatrix = reviewMatrix / np.linalg.norm(reviewMatrix)

		#Add row to feature matrix
		feature_matrix[index] = reviewMatrix

		#Add entry to label matrix
		label_matrix[index] = int(review["overall_quality_score"] * 10)


	return feature_matrix, label_matrix


def generateFeatureMatrixProfLevel(reviews, corpus_dict):

	num_reviews = len(reviews)
	num_features = len(corpus_dict)

	feature_matrix = np.zeros((num_reviews, num_features))
	label_matrix = np.zeros(num_reviews)

	professor_to_review_array = []
	
	for index, review in enumerate(reviews):

		reviewMatrix = np.zeros(num_features)

		for word in review['comment']: 				       
			if word in corpus_dict:
				reviewMatrix[corpus_dict[word]] += 1
		
		
		# np.set_printoptions(threshold=np.nan)

		# Normalize
		reviewMatrix = reviewMatrix / np.linalg.norm(reviewMatrix)
		
		# Add row to feature matrix
		feature_matrix[index] = reviewMatrix

		# Add entry to label matrix
		label_matrix[index] = int(review["overall_quality_score"] * 10)

		professor_to_review_array.append(review["prof_id"])

	return feature_matrix, label_matrix, professor_to_review_array


def generateClassifier(features, labels, C=.1):

	#Create SVM object
	clf = LinearSVC(C=C)

	#Fit to training data
	clf.fit(features, labels)

	return clf


def runSVM(processed_professors, corpus_dict, mode, C, classification):

	#Total number of features
	num_features = len(corpus_dict) + 3

	#Select a training and testing set
	total_test_features = list()
	total_accuracy = 0

	for k in range(5):
		training_reviews, testing_reviews, test_prof_scores = getTrainTestSets(processed_professors, k, classification)
		
		#Get feature and label matrices for training data
		train_feature_matrix, train_label_matrix, garbage = generateFeatureMatrixProfLevel(training_reviews, corpus_dict)
		
		#Train classifier
		clf = generateClassifier(train_feature_matrix, train_label_matrix, C)

		#Get feature and correct label matrices for test data
		test_feature_matrix, correct_labels, professor_to_review_array = generateFeatureMatrixProfLevel(testing_reviews, corpus_dict)

		#Predict
		num_correct_preds = 0.0
		
		predictions = clf.predict(test_feature_matrix)

		# Incrememnt total predictions
		for index, prediction in enumerate(predictions):

			# For review-level classification, compare prediction of individual review
			if classification == "review":
				if prediction/10 >= 3.5 and correct_labels[index]/10 >= 3.5:
					num_correct_preds += 1
				elif prediction/10 < 2.5 and correct_labels[index]/10 < 2.5:
					num_correct_preds += 1

			# For professor-level classification, sum prediction values
			else:
				test_prof_scores[professor_to_review_array[index]] += prediction

		# For professor-level classification, take the average score of all reviews per professor and compare to professor's overall quality score
		if classification == "prof":

			for prof_id, score in test_prof_scores.iteritems():

				if classification == "concat":
					score /= 10

				score /= (10*len(processed_professors[prof_id]['reviews']))

				if score >= 3.5 and processed_professors[prof_id]['overall_quality_score'] >= 3.5:
					num_correct_preds += 1
					print "MATCH:", score, processed_professors[prof_id]['overall_quality_score']

				elif score < 2.5 and processed_professors[prof_id]['overall_quality_score'] < 2.5:
					num_correct_preds += 1
					print "MATCH:", score, processed_professors[prof_id]['overall_quality_score']
				else:
					print "NO MATCH:", score, processed_professors[prof_id]['overall_quality_score']

		if classification == "review":
			accuracy = num_correct_preds / len(correct_labels)
		else:
			accuracy = num_correct_preds / len(test_prof_scores)

		total_accuracy += accuracy

	return total_accuracy/5


def getTrainTestSets(processed_professors, k, classification):

	training_set = list()
	testing_set = list()
	test_prof_scores = dict()
	index = 0
	
	for prof_id, professor in processed_professors.iteritems():

		if index % 5 == k:
			test_prof_scores[prof_id] = 0
			for review_obj in professor["reviews"]:
				testing_set.append(review_obj)
			
		else:
			for review_obj in professor["reviews"]:
				training_set.append(review_obj)
		
		index += 1

	return training_set, testing_set, test_prof_scores



if __name__ == '__main__':

	if len(sys.argv) < 1:
		print "Please enter a mode: 'small' or 'large'"
		print "    small = dataset from Northwestern Polytechnic Institute and Webb Institute"
		print "    large = dataset from University of Michigan"
		exit(1)
	
	mode = sys.argv[1]

	errorCheckMode(mode)

	with open("processed_professors_"+mode+".pkl", 'rb') as processed_prof_file:
		processed_professors = pickle.load(processed_prof_file)

	with open("corpus_dict_"+mode+".pkl", 'rb') as corpus_dict_file:
		corpus_dict = pickle.load(corpus_dict_file)

	c = 0.1
	
	prof_level_accuracy = runSVM(processed_professors, corpus_dict, mode, c, "prof")
	review_level_accuracy = runSVM(processed_professors, corpus_dict, mode, c, "review")

	print "Professor-level classification accuracy:", prof_level_accuracy
	print "Review-level classification accuracy:", review_level_accuracy

