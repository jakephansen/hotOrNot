# PART 2: PROCESS DATA
# Jacob Hansen (jbknill), Joshua Knill (jphans), Tyler Laredo (tlaredo), Gautam Visveswaran (gautamv)

from subprocess import call
import os, pickle
from specificity import *
from opinion_finder import *
from util import *


# If classification is 'prof', the review object will be a professor object and prof_id = review_id
def createReviewObject(review, prof_id, review_id, classification):

	review_object = dict()
	review_object['prof_id'] = prof_id
	review_object['review_id'] = review_id
	review_object['overall_quality_score'] = review['overall_quality_score']
	review_object['num_obj'] = review['num_obj']
	review_object['num_subj'] = review['num_subj']
	review_object['specificity'] = review['specificity']

	if classification == 'prof':
		review_object['comment'] = preprocess(review['all_reviews'])
	elif classification == 'review':
		review_object['comment'] = preprocess(review['comment'])

	return review_object

def createProfReviewsArray(reviews_dict, prof_id):


	reviews = list()
	for review_id, review in reviews_dict.iteritems():
		review_object = createReviewObject(review, prof_id, review_id, 'review')
		reviews.append(review_object)

	return reviews


def processProfessors(professors):

	processed_professors = dict()
	word_count = 0

	for prof_id, professor in professors.iteritems():

		processed_prof = dict()
		processed_prof['reviews'] = createProfReviewsArray(professor['reviews'], prof_id)
		processed_prof['all_reviews'] = createReviewObject(professor, prof_id, prof_id, 'prof')
		processed_prof['overall_quality_score'] = professor['overall_quality_score']

		processed_professors[prof_id] = processed_prof


	return processed_professors


if __name__ == "__main__":
	
	if len(sys.argv) < 1:
		print "Please enter a mode: 'small' or 'large'"
		print "    small = dataset from Northwestern Polytechnic Institute and Webb Institute"
		print "    large = dataset from University of Michigan"
		exit(1)
	
	mode = sys.argv[1]

	errorCheckMode(mode)

	with open("professors_"+mode+".pkl", 'rb') as prof_file:
		professors = pickle.load(prof_file)

	professors = runSpecificity(mode, professors)
	professors = runOpinionFinder(mode, professors)
	processed_professors = processProfessors(professors)

	# Save updated professors dictionary to file
	with open("professors_"+mode+".pkl", 'wb') as prof_file:
		pickle.dump(professors, prof_file, protocol=pickle.HIGHEST_PROTOCOL)

	with open("processed_professors_"+mode+".pkl", 'wb') as processed_profs_file:
		pickle.dump(processed_professors, processed_profs_file, protocol=pickle.HIGHEST_PROTOCOL)

