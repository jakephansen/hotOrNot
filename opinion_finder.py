# OpinionFinder functions for PART 2
# Jacob Hansen (jbknill), Joshua Knill (jphans), Tyler Laredo (tlaredo), Gautam Visveswaran (gautamv)

import os, shutil

# Move files & directories to opinionfinderv2.0 directory prior to running OpinionFinder
def prepareReviewsForOpinionFinder(mode, classification):

	print "Preparing "+classification+"-level files for OpinionFinder..."

	reviews_dir_name = classification+"_level_reviews_"+mode

	if os.path.exists("./opinionfinderv2.0/database/docs/"+reviews_dir_name):
		shutil.rmtree("./opinionfinderv2.0/database/docs/"+reviews_dir_name)

	# Move review files to opinionfinderv2.0 directory
	shutil.copytree(reviews_dir_name, "opinionfinderv2.0/database/docs/"+reviews_dir_name)

	os.chdir("./opinionfinderv2.0")

	filenames_doclist = open(reviews_dir_name+".doclist","w+")

	# Create list of filenames in filenames.doclist
	files = os.listdir("./database/docs/"+reviews_dir_name)
	for name in files:
		filenames_doclist.write("./database/docs/"+reviews_dir_name+"/"+name+'\n')

	filenames_doclist.close()

	os.chdir('..')


# Move review files back to reviews directory in main directory
def cleanFilesAfterOpinionFinder(mode, classification):

	os.chdir("./opinionfinderv2.0")

	print "Cleaning "+classification+"-level files after running OpinionFinder..."

	reviews_dir_name = classification+"_level_reviews_"+mode
	doclist = reviews_dir_name+".doclist"
	
	with open(doclist, 'r') as filenames_doclist:
		for filename in filenames_doclist.readlines():
			path = filename.rstrip()
			os.remove(path)

	filenames_doclist.close()

	os.chdir('..')


# Get prof_id given a directory name
def getProfID(directory_name):
	prof_id = directory_name.split('.')[0]
	prof_id = prof_id.strip("prof")
	return int(prof_id)


# Get review_id given a directory name
def getReviewID(directory_name):
	review_id = directory_name.split('.')[1]
	review_id = review_id.strip("review")
	return int(review_id)


# Return object containing (1) number of subjective sentences and (2) number of objetive sentences
def getSubjectivityCounts():
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

	f.close()
	
	ret_obj = {'num_subj': num_subj, 'num_obj': num_obj}
	return ret_obj


# Updates professors dictionary by including subjectivity counts for all_reviews per professor
def addProfLevelSubjectivityCounts(mode, professors):

	print "Adding professor-level subjectivity counts"

	reviews_dir_name = "prof_level_reviews_"+mode
	os.chdir("./opinionfinderv2.0/database/docs/"+reviews_dir_name+"/")

	for directory in os.listdir('.'):
		if directory.startswith(".DS_"):
			continue

		prof_id = getProfID(directory)
		
		os.chdir(directory)
		subjectivity = getSubjectivityCounts()
		professors[prof_id]['num_subj'] = subjectivity['num_subj']
		professors[prof_id]['num_obj'] = subjectivity['num_obj']
		os.chdir('..')

	os.chdir('../../../..')

	return professors



# Updates professors dictionary by including subjectivity counts for each individual review per professor
def addReviewSubjectivityCounts(mode, professors):

	print "Adding review-level subjectivity counts"

	reviews_dir_name = "review_level_reviews_"+mode
	os.chdir("./opinionfinderv2.0/database/docs/"+reviews_dir_name+"/")

	for directory in os.listdir('.'):
		if directory.startswith(".DS_"):
			continue

		prof_id = getProfID(directory)
		review_id = getReviewID(directory)
		
		os.chdir(directory)
		subjectivity = getSubjectivityCounts()
		professors[prof_id]['reviews'][review_id]['num_subj'] = subjectivity['num_subj']
		professors[prof_id]['reviews'][review_id]['num_obj'] = subjectivity['num_obj']
		os.chdir('..')

	os.chdir('../../../..')

	return professors


# Execute OpinionFinder program
def executeOpinionFinder(mode, classification):

	os.chdir("./opinionfinderv2.0")

	print "Executing OpinionFinder for "+classification+"-level reviews"

	doclist = classification+"_level_reviews_"+mode+".doclist"
	command = "java -Xmx8g -classpath ./lib/weka.jar:./lib/stanford-postagger.jar:opinionfinder.jar opin.main.RunOpinionFinder "+doclist+" -d"

	# Run OpinionFinder command
	os.system(command)

	os.chdir('..')


# Run entire specificity program; called in prepare_reviews
def runOpinionFinder(mode, professors):

	# Prepare files for running OpinionFinder
	prepareReviewsForOpinionFinder(mode, "prof")
	prepareReviewsForOpinionFinder(mode, "review")

	# Execute OpinionFinder
	executeOpinionFinder(mode, "prof")
	executeOpinionFinder(mode, "review")

	# Clean up files after running OpinionFinder
	cleanFilesAfterOpinionFinder(mode, "prof")
	cleanFilesAfterOpinionFinder(mode, "review")

	# Update each professor object in professors w/ prof-level subjectivity counts
	professors = addProfLevelSubjectivityCounts(mode, professors)

	# Update each review object for each professor w/ review-level subjectivity counts
	professors = addReviewSubjectivityCounts(mode, professors)

	print "OpinionFinder complete"

	return professors
