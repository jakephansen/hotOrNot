import pickle, os
from preprocessor import *

# Create an array of review objects
def createReviewsArray(professor_ids, professors, subjectivity_counts, specificity, mode):
	reviews = list()

	for prof_id in professor_ids:

		if "professor" in mode:
			reviews.append(createReview(prof_id, prof_id, professors[prof_id]['overall_quality_score'], subjectivity_counts, specificity[prof_id], mode))

		else:
			for review_id, review in professors[prof_id]['reviews'].iteritems():
				reviews.append(createReview(prof_id, review_id, review['score'], subjectivity_counts, specificity[review_id], mode))
			
	return reviews

# Create review object and write entire corpus to output file
def createReview(prof_id, review_id, review_score, subjectivity_counts, specificity, mode):

	review_filename = ""
	if "professor" in mode:
		review_filename = "prof"+str(prof_id)+".txt"
	else:
		review_filename = "prof"+str(prof_id)+".review"+str(review_id)+".txt"
	
	review = dict()
	
	review['review_id'] = review_id
	review['prof_id'] = prof_id
	review['overall_quality_score'] = review_score
	review['num_obj'] = subjectivity_counts[review_id]['num_obj']
	review['num_subj'] = subjectivity_counts[review_id]['num_subj']
	review['specificity'] = specificity
		
	with open(review_filename, 'r') as review_file:
		comment_untokenized = review_file.read()
	
	review['comment'] = preprocess(comment_untokenized)

	os.chdir('..')
	corpus = open("corpus"+mode+".txt","a")
	for comment in review['comment']:
		corpus.write(comment+'\n')

	if mode == "_professors_test":
		os.chdir('./professors_test')
	elif mode == "_professors":
		os.chdir('./professors')
	elif mode == "_test":
		os.chdir('./reviews_test')
	else:
		os.chdir('./reviews')

	return review

# Print out details surrounding data set
def printDataSetDetails(professor_ids, all_scores, specificity, mode):

	print "Number of professors: ", len(professor_ids)
	print "Number of reviews: ", len(all_scores)
	print "Average score: ", sum(all_scores)/len(all_scores)

	if mode == "_professors_test":
		os.chdir('./professors_test')
	elif mode == "_professors":
		os.chdir('./professors')
	elif mode == "_test":
		os.chdir('./reviews_test')
	else:
		os.chdir('./reviews')
	
	num_review_files = sum([len(files) for r, d, files in os.walk(os.getcwd())])

	print "Number of review files: ", num_review_files

	os.chdir('..')


if __name__ == "__main__":

	# accepts: "test", "professors", "professors_test"
	mode = ""
	if len(sys.argv) > 1:
		mode = "_"+sys.argv[1]

	# Clean up directory
	# if os.path.exists("reviews"+mode+".pkl"):
		# os.remove("reviews"+mode+".pkl")
	if os.path.exists("corpus"+mode+".txt"):
		os.remove("corpus"+mode+".txt")

	corpus = open("corpus"+mode+".txt","w+")

	# Load variables from pickle files

	temp_mode = ""
	if "test" in mode:
		temp_mode = "_test"

	with open("professors"+temp_mode+".pkl", 'rb') as prof_file:
		professors = pickle.load(prof_file)
	with open("professor_ids"+temp_mode+".pkl", 'rb') as prof_ids_file:
		professor_ids = pickle.load(prof_ids_file)
	with open("all_scores"+temp_mode+".pkl", 'rb') as all_scores_file:
		all_scores = pickle.load(all_scores_file)
	

	with open("subjectivity_counts"+mode+".pkl", 'rb') as subjectivity_file:
		subjectivity_counts = pickle.load(subjectivity_file)
	with open("specificity"+mode+".pkl", 'rb') as specificity_file:
		specificity = pickle.load(specificity_file)

	# Print data set details (num professors, num reviews, average score)
	printDataSetDetails(professor_ids, all_scores, specificity, mode)

	# Generate reviews array
	if mode == "_professors_test":
		os.chdir('./professors_test')
	elif mode == "_professors":
		os.chdir('./professors')
	elif mode == "_test":
		os.chdir('./reviews_test')
	else:
		os.chdir('./reviews')
	reviews = createReviewsArray(professor_ids, professors, subjectivity_counts, specificity, mode)
	os.chdir('..')

	# print reviews

	if mode == "_professors_test":
		with open("professors_all_reviews_test.pkl", 'wb') as reviews_file:
			pickle.dump(reviews, reviews_file, protocol=pickle.HIGHEST_PROTOCOL)

	elif mode == "_professors":
		with open("professors_all_reviews.pkl", 'wb') as reviews_file:
			pickle.dump(reviews, reviews_file, protocol=pickle.HIGHEST_PROTOCOL)

	elif mode == "_test":
		with open("reviews_test.pkl", 'wb') as reviews_file:
			pickle.dump(reviews, reviews_file, protocol=pickle.HIGHEST_PROTOCOL)

	else:
		with open("reviews.pkl", 'wb') as reviews_file:
			pickle.dump(reviews, reviews_file, protocol=pickle.HIGHEST_PROTOCOL)


