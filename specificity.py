# Specificity functions for PART 2
# Jacob Hansen (jbknill), Joshua Knill (jphans), Tyler Laredo (tlaredo), Gautam Visveswaran (gautamv)

import os
from preprocessor import *

# Return tokenized comment
def tokenizeComment(comment):
	tokens = tokenizeText(comment)
	return ' '.join(tokens)


# Prepares reviews for speciteller by creating output files returning parallel arrays with info that pertains to each line.
	# For review-level classification (review_level_all_reviews_file), each line in output file contains just one review. Adjacent array `review_info` contains review_id and prof_id that pertains to each line of output file.
	# For professor-level classification (prof_level_all_reviews), each line in output file contains all reviews for each professor (i.e. 1 line per professor). Adjacent array `prof_ids` contains professor id for each line of output file.
def prepareReviewsForSpeciteller(mode, professors):
	
	print "Preparing files for Speciteller..."

	prof_level_all_reviews_file = open("prof_level_all_reviews_"+mode+".txt", 'w+')
	review_level_all_reviews_file = open("review_level_all_reviews_"+mode+".txt", 'w+')

	# List of professor ids parallel to each line in prof_level_all_reviews_file
	prof_ids = list()
	# List of professor & review ids parallel to each line in review_level_all_reviews_file
	review_info = list()

	for prof_id, professor in professors.iteritems():

		prof_ids.append(prof_id)
		tokenized_all_reviews = tokenizeComment(professor['all_reviews'])
		prof_level_all_reviews_file.write(tokenized_all_reviews+'\n')

		for review_id, review in professor['reviews'].iteritems():
			review_info.append({'review_id': review_id, 'prof_id': prof_id})
			tokenized_comment = tokenizeComment(review['comment'])
			if tokenized_comment == "":
				tokenized_comment = "."
			review_level_all_reviews_file.write(tokenized_comment+'\n')

	prof_level_all_reviews_file.close()
	review_level_all_reviews_file.close()

	return prof_ids, review_info


# Updates professors dictionary by including specificity scores for each review and professor
def addSpecificityScores(mode, professors, prof_ids, review_info):

	print "Adding prof-level specificity scores"

	index = 0

	# Iterate over each line in prof_level_specificity_scores and update professor's specificity score for all_reviews
	with open("prof_level_specificity_scores_"+mode+".txt", 'r') as f:
		lines = f.readlines()
		for line in lines:
			prof_id = prof_ids[index]
			professors[prof_id]['specificity'] = float(line.rstrip())
			index += 1
	
	f.close()

	print "Adding review-level specificity scores"

	index = 0
	
	# Iterate over each line in review_level_specificity_scores and update each review's specificity score
	with open("review_level_specificity_scores_"+mode+".txt", 'r') as f:
		lines = f.readlines()
		for line in lines:
			prof_id = review_info[index]['prof_id']
			review_id = review_info[index]['review_id']
			professors[prof_id]['reviews'][review_id]['specificity'] = float(line.rstrip())
			index += 1

	f.close()

	return professors


# Execute Speciteller program
def executeSpeciteller(mode, classification):

	print "Executing Speciteller for "+classification+"-level reviews"

	input_file = classification+"_level_all_reviews_"+mode+".txt"
	output_file = classification+"_level_specificity_scores_"+mode+".txt"

	command = "python speciteller/speciteller.py --inputfile ./"+input_file + " --outputfile " + output_file

	os.system(command)

# Run entire specificity program; called in prepare_reviews
def runSpecificity(mode, professors):

	# Prepare review files & arrays for speciteller library
	prof_ids, review_info = prepareReviewsForSpeciteller(mode, professors)

	# Call speciteller commands for prof_level and review_level classifications
	executeSpeciteller(mode, "prof")
	executeSpeciteller(mode, "review")

	# Update professors dictionary with specificity scores
	professors = addSpecificityScores(mode, professors, prof_ids, review_info)

	print "Specificity complete!"

	return professors

