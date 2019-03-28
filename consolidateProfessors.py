import os, pickle, shutil, sys

if __name__ == "__main__":

	mode = ""
	if len(sys.argv) > 1:
		mode = "_"+sys.argv[1]

	with open("professors"+mode+".pkl", 'rb') as prof_file:
		professors = pickle.load(prof_file)

	with open("professor_ids"+mode+".pkl", 'rb') as prof_ids_file:
		professor_ids = pickle.load(prof_ids_file)

	# Remove professors folder before running
	if os.path.exists("professors"+mode):
		shutil.rmtree("professors"+mode)

	#Create folder for professors
	if not os.path.exists("professors"+mode):
		os.makedirs("professors"+mode)

	os.chdir("./professors"+mode)

	# Iterate over professors and concatente reviews
	for prof_id in professor_ids:
		professor_file = open("prof"+str(prof_id)+".txt", "w+")

		concatenated_reviews = ""

		for review_id, review in professors[prof_id]['reviews'].iteritems():
			# strip review of any whitespace
			concatenated_reviews += review['comment'].replace('\r',"") + " "

		professor_file.write(concatenated_reviews)







