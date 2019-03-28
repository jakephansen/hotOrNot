import os, pickle, shutil

# Runs opinion finder
def runOpinionFinder():
	# Move review files to opinion finder directory
	shutil.move("./professors_test", "./opinionfinderv2.0/database/docs")

	# Make duplicate reviewsTest directory
	os.mkdir('./professors_test')

	os.chdir("./opinionfinderv2.0")

	filenames_doclist = open("filenames_professors_test.doclist","w+")

	# Create list of filenames in filenames.doclist
	files = os.listdir("./database/docs/professors_test")
	for name in files:
		filenames_doclist.write("database/docs/professors_test/"+name+'\n')

	filenames_doclist.close()

	# Run opinion finder command
	os.system("java -Xmx8g -classpath ./lib/weka.jar:./lib/stanford-postagger.jar:opinionfinder.jar opin.main.RunOpinionFinder filenames_professors_test.doclist -d")
	
	# Move review files back to reviewsTest in main directory
	with open("filenames_professors_test.doclist", 'r') as filenames_doclist:
		for filename in filenames_doclist.readlines():
			path = filename.rstrip()
			shutil.move(path, "../professors_test")

	filenames_doclist.close()

	os.chdir('..')

# Return object containing (1) number of subjective sentences and (2) number of objetive sentences
def getSubjectivity():
	num_subj = 0
	num_obj = 0
	with open("sent_subj.txt", 'r') as f:
		for line in f.readlines():
			line = line.rstrip()

			code = line.split()[1]
			if code == "subj":
				num_subj += 1
			else:
				num_obj += 1

	ret_obj = {'num_subj': num_subj, 'num_obj': num_obj}
	return ret_obj

# Get review id given a directory name
def getProfID(directory_name):
	prof_id = directory_name.split('.')[0]
	prof_id = prof_id.strip("prof")
	return int(prof_id)

# Populate subjectivity counts dictionary
def collectSubjectivityCounts():
	subjectivity_counts = dict()

	os.chdir("./opinionfinderv2.0/database/docs/professors_test/")

	for directory in os.listdir('.'):
		if directory.startswith(".DS_"):
			continue

		prof_id = getProfID(directory)
		os.chdir(directory)
		subjectivity_counts[prof_id] = getSubjectivity()
		os.chdir('..')

	os.chdir('../../../..')

	return subjectivity_counts


if __name__ == "__main__":

	runOpinionFinder()

	subjectivity_counts = collectSubjectivityCounts()

	if os.path.exists("subjectivity_counts_professors_test.pkl"):
		os.remove("subjectivity_counts_professors_test.pkl")

	# Save subjectivity counts to file
	with open('subjectivity_counts_professors_test.pkl', 'wb') as subjectivity_file:
		pickle.dump(subjectivity_counts, subjectivity_file, protocol=pickle.HIGHEST_PROTOCOL)





	

